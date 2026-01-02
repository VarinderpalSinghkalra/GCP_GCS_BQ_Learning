import os
import base64
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------
# Config (safe defaults)
# -------------------------------------------------
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "data-engineering-479617")
TOPIC_ID = os.environ.get("ISSUES_TOPIC", "issues-topic")

# -------------------------------------------------
# Pub/Sub client
# -------------------------------------------------
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# -------------------------------------------------
# Flask app (REQUIRED for Gunicorn)
# -------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def generate_issue_id() -> str:
    return f"INC-{uuid.uuid4().hex[:8].upper()}"

def publish_to_pubsub(message: dict):
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data=data)
    message_id = future.result()
    logging.info(f"Published to Pub/Sub: {message_id}")
    return message_id

# -------------------------------------------------
# Main handler
# -------------------------------------------------
@app.route("/", methods=["POST"])
def handler():
    try:
        payload = request.get_json(silent=True)
        logging.info("Incoming request received")

        # -------------------------------------------------
        # CASE 1: Eventarc (Firestore → Eventarc → Cloud Run)
        # -------------------------------------------------
        if payload and "data" in payload:
            decoded = base64.b64decode(payload["data"]).decode(
                "utf-8", errors="ignore"
            )

            event_message = {
                "issue_id": f"FS-{uuid.uuid4().hex[:8].upper()}",
                "source": "firestore-eventarc",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "payload": decoded  # STRING (safe for BigQuery)
            }

            publish_to_pubsub(event_message)
            return ("OK", 204)

        # -------------------------------------------------
        # CASE 2: Manual API / curl
        # -------------------------------------------------
        if payload:
            issue_id = generate_issue_id()

            issue_event = {
                "issue_id": issue_id,
                "source": "manual-api",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "payload": json.dumps(payload)  # 🔑 MUST BE STRING
            }

            publish_to_pubsub(issue_event)

            return jsonify({
                "issue_id": issue_id,
                "status": "created",
                "message": "Issue published to Pub/Sub"
            }), 200

        return jsonify({"error": "Empty request body"}), 400

    except Exception:
        logging.exception("Request processing failed")
        return jsonify({"error": "Internal server error"}), 500
