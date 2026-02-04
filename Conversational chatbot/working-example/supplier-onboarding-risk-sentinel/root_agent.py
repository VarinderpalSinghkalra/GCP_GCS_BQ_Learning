import uuid
from google.cloud import storage

from tools.normalization_tool import (
    normalize_supplier_name,
    normalize_country
)
from tools.firestore_tool import (
    create_supplier,
    update_supplier,
    create_supplier_master,
    find_supplier_by_match_key,
    add_approved_document
)
from tools.gcs_tool import upload_approved_document
from tools.email_tool import send_email
from tools.adk_agent_executor import execute_agent

from rules.tax_form_rules import get_required_tax_form
from rules.risk_rules import classify_risk

from agents.document_collection_agent import document_collection_agent
from agents.document_validation_agent import document_validation_agent
from agents.compliance_agent import compliance_agent
from agents.risk_scoring_agent import risk_scoring_agent
from agents.legal_review_agent import legal_review_agent
from agents.notification_agent import notification_agent

from agents.negotiation_agent import commercial_suggestion  # advisory only
from tools.w9_cover_page_tool import generate_w9_with_cover
from tools.quotation_gcs_tool import store_quotation_email


# --------------------------------------------------
# CONFIG
# --------------------------------------------------
W9_TEMPLATE_URI = "gs://contracts-demo-277069041958/fw9.pdf"
SANCTIONED_COUNTRIES = {"IR", "KP", "SY", "CU", "RU"}


def load_gcs_file(gcs_uri: str) -> bytes:
    client = storage.Client()
    _, _, bucket_name, *path = gcs_uri.split("/")
    blob = client.bucket(bucket_name).blob("/".join(path))

    if not blob.exists():
        raise FileNotFoundError(f"File not found at {gcs_uri}")

    return blob.download_as_bytes()


def should_send_notification(decision: str) -> bool:
    return decision in {"APPROVED", "MANUAL_REVIEW", "REJECTED"}


# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------
def onboard_supplier(payload: dict) -> dict:
    request_id = str(uuid.uuid4())

    # 1️⃣ Normalize supplier
    normalized = normalize_supplier_name(payload["supplier_name"])
    match_key = normalized["match_key"]

    existing = find_supplier_by_match_key(match_key)
    if existing:
        return {
            "request_id": request_id,
            "status": "DUPLICATE",
            "supplier_id": existing["supplier_id"]
        }

    supplier_id = str(uuid.uuid4())
    country = normalize_country(payload["country"])

    # 2️⃣ Tax form
    tax_form = get_required_tax_form(
        country,
        payload.get("supplier_type", "COMPANY")
    )

    # 3️⃣ Firestore base
    create_supplier_master(
        supplier_id,
        {
            "supplier_id": supplier_id,
            "original_name": payload["supplier_name"],
            "normalized_name": normalized["normalized_name"],
            "match_key": match_key
        }
    )

    create_supplier(
        supplier_id,
        {
            "supplier_id": supplier_id,
            "name": normalized["normalized_name"],
            "country": country,
            "tax_form": tax_form,
            "status": "ONBOARDING"
        }
    )

    # 4️⃣ Agent pipeline
    documents = execute_agent(document_collection_agent, payload)
    validations = execute_agent(document_validation_agent, documents)
    execute_agent(compliance_agent, validations)

    risk = execute_agent(
        risk_scoring_agent,
        {"supplier_name": normalized["normalized_name"], "country": country}
    )

    risk_score = int(risk.get("risk_score", 20))
    risk_reason = risk.get("risk_reason", "Default risk logic")
    risk_level = classify_risk(risk_score)

    quotation_gcs_uri = None
    commercial_ai_suggestion = None

    # 5️⃣ HARD STOP — SANCTIONS
    if country in SANCTIONED_COUNTRIES:
        decision = "REJECTED"
        risk_level = "HIGH"
        risk_score = 90
        risk_reason = "Sanctioned country"

        legal_review = {
            "status": "NOT_APPLICABLE",
            "review": "Supplier belongs to a sanctioned country",
            "risk_reason": risk_reason
        }

    # 6️⃣ NON-SANCTIONED FLOW
    else:
        # 📦 Store quotation email if present
        if payload.get("raw_email"):
            quotation_gcs_uri = store_quotation_email(
                supplier_id=supplier_id,
                rfq_id=payload.get("rfq_id", "UNKNOWN_RFQ"),
                raw_email=payload["raw_email"],
                metadata={
                    "supplier_id": supplier_id,
                    "country": country,
                    "stage": "RFQ_OPEN"
                }
            )

        # 🧠 Advisory AI only (no decision power)
        if quotation_gcs_uri:
            commercial_ai_suggestion = commercial_suggestion(
                {
                    "supplier_id": supplier_id,
                    "supplier_name": normalized["normalized_name"],
                    "country": country,
                    "quotation_gcs_uri": quotation_gcs_uri
                }
            )

        # 🔑 FINAL DECISION LOGIC (CORRECT)
        if quotation_gcs_uri:
            # RFQ still open → cannot approve
            decision = "MANUAL_REVIEW"
            legal_review = {
                "status": "PENDING",
                "review": "Quotation received; RFQ negotiation pending"
            }

        elif risk_level == "LOW":
            decision = "APPROVED"
            legal_review = {
                "status": "COMPLETED",
                "review": "No legal issues identified"
            }

        elif risk_level == "MEDIUM":
            decision = "MANUAL_REVIEW"
            legal_review = execute_agent(
                legal_review_agent,
                {"country": country, "risk_reason": risk_reason}
            )

        else:
            decision = "REJECTED"
            legal_review = execute_agent(
                legal_review_agent,
                {"country": country, "risk_reason": risk_reason}
            )

    # 7️⃣ Documents
    if decision in {"APPROVED", "MANUAL_REVIEW"}:
        if tax_form == "W-9" and country == "US":
            template_bytes = load_gcs_file(W9_TEMPLATE_URI)
            final_pdf = generate_w9_with_cover(
                template_bytes, normalized["normalized_name"]
            )

            gcs_uri = upload_approved_document(
                supplier_id,
                "W-9",
                "W-9-DRAFT.pdf",
                final_pdf,
                "application/pdf",
                "attachment; filename=W-9-DRAFT.pdf"
            )
        else:
            gcs_uri = upload_approved_document(
                supplier_id,
                tax_form,
                f"{tax_form}.pdf",
                documents[tax_form]["file_bytes"],
                "application/pdf",
                f"attachment; filename={tax_form}.pdf"
            )

        if gcs_uri:
            add_approved_document(supplier_id, tax_form, gcs_uri)

    # 8️⃣ Email
    if should_send_notification(decision):
        email = execute_agent(
            notification_agent,
            {
                "supplier": normalized["normalized_name"],
                "decision": decision,
                "risk_level": risk_level,
                "country": country,
                "is_sanctioned": country in SANCTIONED_COUNTRIES,
                "commercial_ai_suggestion": commercial_ai_suggestion
            }
        )

        recipients = list(set(email.get("recipients", [])))
        if recipients:
            send_email(recipients, email["subject"], email["body"])

    # 9️⃣ Final Firestore update
    update_supplier(
        supplier_id,
        {
            "status": decision,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_reason": risk_reason,
            "legal_review": legal_review,
            "commercial_ai_suggestion": commercial_ai_suggestion,
            "quotation_gcs_uri": quotation_gcs_uri
        }
    )

    return {
        "request_id": request_id,
        "supplier_id": supplier_id,
        "decision": decision,
        "risk_level": risk_level,
        "quotation_gcs_uri": quotation_gcs_uri,
        "commercial_ai_suggestion": commercial_ai_suggestion
    }
