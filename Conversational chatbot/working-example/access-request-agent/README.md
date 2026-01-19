# Access Request Provisioning Agent

## Resources Used
- Firestore: access_requests
- Pub/Sub: access-requests-topic
- Cloud Tasks: access-request-queue

## Lifecycle
new → assigned → in_progress → completed (3 minutes)

## Endpoints

### Submit Access Request
POST /submit_access_request
```json
{
  "user_id": "emp_123",
  "resource": "BigQuery Dataset",
  "access_level": "read",
  "justification": "Reporting access"
}
