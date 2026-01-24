import uuid
from google.cloud import storage

from tools.normalization_tool import normalize_supplier_name
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

from tools.w9_cover_page_tool import generate_w9_with_cover


# ✅ Your confirmed W-9 template (NON-FILLABLE)
W9_TEMPLATE_URI = "gs://contracts-demo-277069041958/fw9.pdf"


def load_gcs_file(gcs_uri: str) -> bytes:
    client = storage.Client()
    _, _, bucket_name, *path = gcs_uri.split("/")
    blob = client.bucket(bucket_name).blob("/".join(path))

    if not blob.exists():
        raise FileNotFoundError(f"W-9 template not found at {gcs_uri}")

    return blob.download_as_bytes()


def onboard_supplier(payload: dict) -> dict:
    request_id = str(uuid.uuid4())

    # --------------------------------------------------
    # 1️⃣ Normalize supplier name
    # --------------------------------------------------
    normalized = normalize_supplier_name(payload["supplier_name"])
    match_key = normalized["match_key"]

    existing = find_supplier_by_match_key(match_key)
    if existing:
        return {
            "request_id": request_id,
            "status": "DUPLICATE",
            "supplier_id": existing["supplier_id"],
            "normalized_name": normalized["normalized_name"],
            "match_key": match_key
        }

    supplier_id = str(uuid.uuid4())

    # --------------------------------------------------
    # 2️⃣ Determine tax form
    # --------------------------------------------------
    tax_form = get_required_tax_form(
        payload["country"],
        payload.get("supplier_type", "COMPANY")
    )

    # --------------------------------------------------
    # 3️⃣ Create base Firestore records
    # --------------------------------------------------
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
            "country": payload["country"],
            "tax_form": tax_form,
            "status": "ONBOARDING"
        }
    )

    # --------------------------------------------------
    # 4️⃣ Run agent pipeline
    # --------------------------------------------------
    documents = execute_agent(document_collection_agent, payload)
    validations = execute_agent(document_validation_agent, documents)
    compliance = execute_agent(compliance_agent, validations)

    risk = execute_agent(
        risk_scoring_agent,
        {
            "supplier_name": normalized["normalized_name"],
            "country": payload["country"]
        }
    )

    risk_score = int(risk.get("risk_score", 20))
    risk_reason = risk.get("risk_reason", "Default risk logic")
    risk_level = classify_risk(risk_score)

    # --------------------------------------------------
    # 5️⃣ Decision logic
    # --------------------------------------------------
    if risk_reason == "Sanctioned country":
        decision = "REJECTED"
        legal_review = {
            "status": "NOT_APPLICABLE",
            "review": "Legal review not applicable due to sanctions restrictions"
        }

    elif risk_level == "LOW":
        decision = "APPROVED"
        legal_review = {
            "status": "COMPLETED",
            "review": "Standard legal review completed; no legal issues identified"
        }

    elif risk_level == "MEDIUM":
        decision = "MANUAL_REVIEW"
        legal_review = execute_agent(
            legal_review_agent,
            {"country": payload["country"], "risk_reason": risk_reason}
        )

    else:
        decision = "REJECTED"
        legal_review = execute_agent(
            legal_review_agent,
            {"country": payload["country"], "risk_reason": risk_reason}
        )

    # --------------------------------------------------
    # 6️⃣ Store approved documents in GCS
    #     ✅ W-9 WITH SUPPLIER NAME (COVER PAGE)
    # --------------------------------------------------
    if decision in ["APPROVED", "MANUAL_REVIEW"]:

        if tax_form == "W-9" and payload["country"] == "US":
            template_bytes = load_gcs_file(W9_TEMPLATE_URI)

            # ✅ SAFE: add supplier name via cover page
            final_pdf_bytes = generate_w9_with_cover(
                original_w9_bytes=template_bytes,
                supplier_name=normalized["normalized_name"]
            )

            gcs_uri = upload_approved_document(
                supplier_id=supplier_id,
                document_type="W-9",
                filename="W-9-DRAFT.pdf",
                file_bytes=final_pdf_bytes,
                content_type="application/pdf",
                content_disposition="attachment; filename=W-9-DRAFT.pdf"
            )

        else:
            gcs_uri = upload_approved_document(
                supplier_id=supplier_id,
                document_type=tax_form,
                filename=f"{tax_form}.pdf",
                file_bytes=documents[tax_form]["file_bytes"],
                content_type="application/pdf",
                content_disposition=f"attachment; filename={tax_form}.pdf"
            )

        if gcs_uri:
            add_approved_document(
                supplier_id=supplier_id,
                document_type=tax_form,
                gcs_uri=gcs_uri
            )

    # --------------------------------------------------
    # 7️⃣ Email notification
    # --------------------------------------------------
    email = execute_agent(
        notification_agent,
        {
            "supplier": normalized["normalized_name"],
            "decision": decision,
            "risk_level": risk_level
        }
    )

    send_email(
        email.get("recipients", []),
        email.get("subject", "Supplier Onboarding Decision"),
        email.get("body", "Supplier onboarding completed.")
    )

    # --------------------------------------------------
    # 8️⃣ Final Firestore update
    # --------------------------------------------------
    update_supplier(
        supplier_id,
        {
            "status": decision,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_reason": risk_reason,
            "legal_review": legal_review,
            "w9_status": "DRAFT_WITH_SUPPLIER_NAME" if tax_form == "W-9" else None
        }
    )

    # --------------------------------------------------
    # 9️⃣ API Response
    # --------------------------------------------------
    return {
        "request_id": request_id,
        "supplier_id": supplier_id,
        "normalized_name": normalized["normalized_name"],
        "match_key": match_key,
        "tax_form": tax_form,
        "risk_level": risk_level,
        "decision": decision
    }

