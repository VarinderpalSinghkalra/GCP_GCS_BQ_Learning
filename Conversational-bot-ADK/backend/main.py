import json
import traceback
from google.cloud import firestore
from google.cloud import pubsub_v1
from datetime import datetime

PROJECT_ID = "data-engineering-479617"
ISSUES_COL = "issues"
PUBSUB_TOPIC = "issues-topic"

db = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)


def update_issue_status(request):
    try:
        body = request.get_json()
        issue_id = body["issue_id"]
        status = body["status"]

        ref = db.collection(ISSUES_COL).document(issue_id)
        snap = ref.get()

        old_status = snap.get("status")

        ref.update({
            "status": status,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        publisher.publish(
            topic_path,
            json.dumps({
                "issue_id": issue_id,
                "old_status": old_status,
                "new_status": status,
                "source": "cloud_tasks",
                "changed_at": datetime.utcnow().isoformat() + "Z",
            }).encode()
        )

        return ("OK", 200)

    except Exception:
        traceback.print_exc()
        return ("FAILED", 200)
