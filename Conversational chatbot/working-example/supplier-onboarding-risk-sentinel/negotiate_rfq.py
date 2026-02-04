from google.cloud import bigquery
from agents.negotiation_agent import negotiate_multiple_quotes

client = bigquery.Client()

def negotiate_rfq_handler(payload: dict):
    rfq_id = payload.get("rfq_id")
    if not rfq_id:
        return {"error": "rfq_id is required"}, 400

    query = """
    SELECT
      supplier_id,
      price,
      delivery_days,
      payment_terms
    FROM supplier_quotations
    WHERE rfq_id = @rfq_id
    """

    job = client.query(
        query,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("rfq_id", "STRING", rfq_id)
            ]
        )
    )

    rows = list(job.result())

    if len(rows) < 2:
        return {
            "rfq_id": rfq_id,
            "status": "INSUFFICIENT_QUOTES",
            "message": "At least 2 quotations required for negotiation"
        }

    # 🔥 NEGOTIATION AGENT
    recommendation = negotiate_multiple_quotes(rows)

    return {
        "rfq_id": rfq_id,
        "quotes_received": len(rows),
        "recommendation": recommendation
    }
