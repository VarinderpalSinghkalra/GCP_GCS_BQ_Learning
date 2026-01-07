# main.py
import os
import logging
import threading
from typing import Dict, Any, List, Optional

import sqlglot
from sqlglot import exp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------
# CONFIG
# ------------------------------
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "data-engineering-479617")
DATASET = os.environ.get("BQ_DATASET", "conversational_demo")
TABLE = os.environ.get("BQ_TABLE", "sample_spenddata")

FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET}.{TABLE}"
GEMINI_MODEL = os.environ.get("GENAI_MODEL", "gemini-2.5-pro")

# ------------------------------
# GLOBAL CLIENTS & CACHES
# ------------------------------
bq_client = None
gemini_model = None

# Schema cache (once per container)
TABLE_SCHEMA: Dict[str, str] = {}

# Aggressive in-memory query cache
QUERY_RESULT_CACHE: Dict[str, List[Dict[str, Any]]] = {}

# ------------------------------
# DIMENSION REGISTRY (SAFE LIST)
# ------------------------------
DIMENSION_KEYWORDS = {
    "business unit": "business_unit",
    "business segment": "business_segment",
    "category": "category",
    "buyer": "buyer",
    "supplier": "supplier",
    "vendor": "supplier",
    "buying channel": "buying_channel",
}

# ------------------------------
# CLIENTS
# ------------------------------
def ensure_clients():
    global bq_client
    if bq_client is None:
        from google.cloud import bigquery
        bq_client = bigquery.Client(project=PROJECT_ID)


def get_gemini():
    """
    Gemini client is created lazily and used ONLY in async background tasks.
    Never blocks the request path.
    """
    global gemini_model
    if gemini_model:
        return gemini_model

    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel

        vertexai.init(project=PROJECT_ID, location="us-central1")
        gemini_model = GenerativeModel(GEMINI_MODEL)
        return gemini_model

    except Exception as e:
        logger.warning("Gemini unavailable: %s", e)
        return None


# ------------------------------
# SCHEMA (LOAD ONCE)
# ------------------------------
def load_schema_once():
    if TABLE_SCHEMA:
        return

    ensure_clients()
    table = bq_client.get_table(FULL_TABLE_ID)

    for field in table.schema:
        TABLE_SCHEMA[field.name.lower()] = field.field_type.upper()

    logger.info("Schema cached with %d columns", len(TABLE_SCHEMA))


# Load schema at container startup (warm instance = fast)
load_schema_once()

# ------------------------------
# SAFE METRICS
# ------------------------------
def safe_sum(column: str) -> str:
    col_type = TABLE_SCHEMA.get(column.lower(), "")
    if col_type in {"INT64", "FLOAT64", "NUMERIC", "BIGNUMERIC"}:
        return f"COALESCE(SUM({column}), 0)"
    return f"COALESCE(SUM(SAFE_CAST({column} AS NUMERIC)), 0)"


def resolve_metric(question: str) -> str:
    q = question.lower()

    if "count" in q or "how many" in q:
        return "COUNT(*) AS count"

    if "volume" in q and "quantity" in TABLE_SCHEMA:
        return f"{safe_sum('quantity')} AS volume"

    if "savings" in q and "savings_amt" in TABLE_SCHEMA:
        return f"{safe_sum('savings_amt')} AS savings"

    return f"{safe_sum('amt_local')} AS spend"


# ------------------------------
# DIMENSION DETECTION
# ------------------------------
def resolve_dimension(question: str) -> Optional[str]:
    q = question.lower()
    for keyword, column in DIMENSION_KEYWORDS.items():
        if keyword in q and column in TABLE_SCHEMA:
            return column
    return None


# ------------------------------
# DATE FILTER (FAST + FAIL-OPEN)
# ------------------------------
def build_time_filter(question: str) -> str:
    q = question.lower()

    po_expr = """
    COALESCE(
        SAFE_CAST(PO_DT AS DATE),
        SAFE.PARSE_DATE('%Y-%m-%d', PO_DT),
        SAFE.PARSE_DATE('%d-%m-%Y', PO_DT),
        SAFE.PARSE_DATE('%Y%m%d', PO_DT)
    )
    """

    if "last 12 months" in q or "last year" in q:
        return f"""
        (
          (SELECT COUNT(*) FROM `{FULL_TABLE_ID}` WHERE {po_expr} IS NOT NULL) = 0
          OR
          {po_expr} >= DATE_SUB(
              (SELECT MAX({po_expr}) FROM `{FULL_TABLE_ID}`),
              INTERVAL 12 MONTH
          )
        )
        """

    return ""


# ------------------------------
# SQL GENERATION
# ------------------------------
def generate_sql(question: str) -> str:
    metric = resolve_metric(question)
    dimension = resolve_dimension(question)
    time_filter = build_time_filter(question)

    select_parts = []
    group_by = ""

    if dimension:
        select_parts.append(dimension)
        group_by = f"\nGROUP BY {dimension}"

    select_parts.append(metric)

    sql = f"""
    SELECT
        {", ".join(select_parts)}
    FROM `{FULL_TABLE_ID}`
    """

    if time_filter:
        sql += f"\nWHERE {time_filter}"

    if group_by:
        sql += group_by

    return sql.strip()


# ------------------------------
# SQL VALIDATION (SECURITY)
# ------------------------------
def validate_sql_ast(sql: str):
    tree = sqlglot.parse_one(sql, read="bigquery")

    for table in tree.find_all(exp.Table):
        if table.name.lower() != TABLE.lower():
            raise ValueError(f"Unauthorized table used: {table.name}")

    for col in tree.find_all(exp.Column):
        if col.name.lower() not in TABLE_SCHEMA:
            raise ValueError(f"Unknown column detected: {col.name}")


# ------------------------------
# QUERY EXECUTION (CACHED)
# ------------------------------
def run_query_cached(sql: str) -> List[Dict[str, Any]]:
    if sql in QUERY_RESULT_CACHE:
        logger.info("Cache hit")
        return QUERY_RESULT_CACHE[sql]

    logger.info("Cache miss → executing BigQuery")
    job = bq_client.query(sql)
    rows = [dict(row) for row in job.result()]
    QUERY_RESULT_CACHE[sql] = rows
    return rows


# ------------------------------
# CONFIDENCE SCORE
# ------------------------------
def confidence_score(sql: str) -> float:
    score = 0.9
    if "group by" in sql.lower():
        score += 0.05
    if "safe_cast" in sql.lower() or "safe.parse_date" in sql.lower():
        score += 0.05
    return round(min(score, 1.0), 2)


# ------------------------------
# ASYNC GEMINI (NON-BLOCKING)
# ------------------------------
def run_gemini_async(question: str, sql: str):
    """
    Runs AFTER response is sent.
    Used only for explanations & suggestions.
    """
    try:
        model = get_gemini()
        if not model:
            return

        prompt = f"""
You are an analytics assistant.

User question:
{question}

Task:
1. Explain the result in simple business language.
2. Suggest 2 follow-up analytical questions.

Rules:
- Do NOT generate SQL
- Do NOT mention tables or columns
- Keep it short
"""

        response = model.generate_content(prompt)
        insight = response.text.strip()

        logger.info("Gemini async insight: %s", insight)

    except Exception:
        logger.exception("Gemini async task failed")


# ------------------------------
# MAIN AGENT (FAST PATH)
# ------------------------------
def ask_agent(question: str) -> Dict[str, Any]:
    sql = generate_sql(question)
    validate_sql_ast(sql)
    rows = run_query_cached(sql)

    # 🔥 Async Gemini (never blocks)
    threading.Thread(
        target=run_gemini_async,
        args=(question, sql),
        daemon=True
    ).start()

    warnings = []
    if resolve_dimension(question) is None and "by" in question.lower():
        warnings.append("Requested grouping not recognized; returning overall metric.")

    return {
        "question": question,
        "sql": sql,
        "rows": rows,
        "confidence_score": confidence_score(sql),
        "warnings": warnings,
        "cache_size": len(QUERY_RESULT_CACHE),
    }


# ------------------------------
# HTTP ENTRY POINT
# ------------------------------
def entry_point(request):
    from flask import jsonify, make_response

    # CORS preflight
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

    try:
        payload = request.get_json(silent=True) or {}
        question = payload.get("question", "").strip()

        if not question:
            resp = make_response(jsonify({"error": "Missing question"}), 400)
        else:
            resp = make_response(jsonify(ask_agent(question)), 200)

        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return resp

    except Exception as e:
        logger.exception("Execution error")
        resp = make_response(jsonify({"error": str(e)}), 500)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
