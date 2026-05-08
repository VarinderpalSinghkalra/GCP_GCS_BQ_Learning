# Google Cloud Pub/Sub – Complete Practical Commands Guide
# Introduction
Google Cloud Pub/Sub is a fully managed messaging service that enables asynchronous communication between applications and services.
Pub/Sub follows a Publisher → Topic → Subscription → Subscriber model.
---
# Configure Project
## Set Active Project
```bash
gcloud config set project YOUR_PROJECT_ID

⸻

Verify Project

gcloud config list

⸻

Pub/Sub Topics

Create Topic

gcloud pubsub topics create orders-topic

⸻

Create Multiple Topics

gcloud pubsub topics create payments-topic
gcloud pubsub topics create inventory-topic

⸻

List Topics

gcloud pubsub topics list

⸻

Describe Topic

gcloud pubsub topics describe orders-topic

⸻

Delete Topic

gcloud pubsub topics delete orders-topic

⸻

Pub/Sub Subscriptions

Create Pull Subscription

gcloud pubsub subscriptions create orders-sub \
    --topic=orders-topic

⸻

Create Push Subscription

gcloud pubsub subscriptions create orders-push-sub \
    --topic=orders-topic \
    --push-endpoint=https://example.com/push

⸻

List Subscriptions

gcloud pubsub subscriptions list

⸻

Describe Subscription

gcloud pubsub subscriptions describe orders-sub

⸻

Delete Subscription

gcloud pubsub subscriptions delete orders-sub

⸻

Publishing Messages

Publish Single Message

gcloud pubsub topics publish orders-topic \
    --message="New order created"

⸻

Publish Multiple Messages

gcloud pubsub topics publish orders-topic \
    --message="Order 1001"
gcloud pubsub topics publish orders-topic \
    --message="Order 1002"
gcloud pubsub topics publish orders-topic \
    --message="Order 1003"

⸻

Publish Message with Attributes

gcloud pubsub topics publish orders-topic \
    --message="Order processed" \
    --attribute=order_id=1001,status=SUCCESS

⸻

Pulling Messages

Pull Single Message

gcloud pubsub subscriptions pull orders-sub \
    --auto-ack

⸻

Pull Multiple Messages

gcloud pubsub subscriptions pull orders-sub \
    --limit=10 \
    --auto-ack

⸻

Pull Without ACK

gcloud pubsub subscriptions pull orders-sub

⸻

Acknowledging Messages

ACK Message

gcloud pubsub subscriptions ack MESSAGE_ACK_ID \
    --subscription=orders-sub

⸻

Message Retention

Create Subscription with Retention

gcloud pubsub subscriptions create orders-retention-sub \
    --topic=orders-topic \
    --message-retention-duration=7d

⸻

Dead Letter Queue (DLQ)

Create Dead Letter Topic

gcloud pubsub topics create dead-letter-topic

⸻

Create Subscription with DLQ

gcloud pubsub subscriptions create orders-dlq-sub \
    --topic=orders-topic \
    --dead-letter-topic=dead-letter-topic \
    --max-delivery-attempts=5

⸻

Ordering Keys

Create Topic with Ordering

gcloud pubsub topics create ordered-topic \
    --message-ordering

⸻

Ordering subscription

gcloud pubsub subscriptions create ordered-sub \
    --topic=ordered-topic

Publish Ordered Message

gcloud pubsub topics publish ordered-topic \
    --message="User event" \
    --ordering-key=user-1001

⸻

IAM Permissions

Add Pub/Sub Publisher Role

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:user@example.com" \
    --role="roles/pubsub.publisher"

⸻

Add Pub/Sub Subscriber Role

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:user@example.com" \
    --role="roles/pubsub.subscriber"

⸻

Snapshots

Create Snapshot

gcloud pubsub snapshots create orders-snapshot \
    --subscription=orders-sub

⸻

List Snapshots

gcloud pubsub snapshots list

⸻

Delete Snapshot

gcloud pubsub snapshots delete orders-snapshot

⸻

Seek Operations

Seek Subscription to Snapshot

gcloud pubsub subscriptions seek orders-sub \
    --snapshot=orders-snapshot

⸻

Filtering Messages

Create Filtered Subscription

gcloud pubsub subscriptions create filtered-sub \
    --topic=orders-topic \
    --message-filter='attributes.status="SUCCESS"'

⸻

Retry Policies

Create Subscription with Retry Policy

gcloud pubsub subscriptions create retry-sub \
    --topic=orders-topic \
    --min-retry-delay=10s \
    --max-retry-delay=600s

⸻

Exactly Once Delivery

Create Subscription with Exactly Once Delivery

gcloud pubsub subscriptions create exactly-once-sub \
    --topic=orders-topic \
    --enable-exactly-once-delivery

⸻

Pub/Sub Emulator

Start Emulator

gcloud beta emulators pubsub start

⸻

Set Emulator Environment

$(gcloud beta emulators pubsub env-init)

⸻

Monitoring Commands

View Subscription Backlog

gcloud pubsub subscriptions describe orders-sub

⸻

Real-Time Architecture

Application → Pub/Sub → Dataflow → BigQuery → Dashboard

⸻

Common Use Cases

* Real-time analytics
* Streaming pipelines
* Event-driven systems
* Log ingestion
* IoT event processing
* Notification systems

⸻

Best Practices

* Use Dead Letter Queues
* Implement ACK properly
* Use message filtering
* Monitor subscription backlog
* Design idempotent consumers
* Use ordering keys only when necessary

⸻

Common Errors

Permission Denied

Cause:

* Missing IAM role

Fix:

* Add Pub/Sub roles

⸻

Topic Not Found

Cause:

* Topic does not exist

Fix:

* Create topic first

⸻

No Messages Received

Cause:

* Wrong subscription
* Message already ACKed

Fix:

* Verify subscription

⸻

Pub/Sub vs Kafka

Feature	Pub/Sub	Kafka
Managed	Fully managed	Self-managed
Scaling	Automatic	Manual
Infrastructure	No setup	Requires clusters
Maintenance	Minimal	High

⸻

Final Summary

Google Cloud Pub/Sub is a scalable messaging and event ingestion service used to build event-driven and real-time architectures.

It supports:

* Topics
* Subscriptions
* Push/Pull messaging
* Ordering
* Dead Letter Queues
* Streaming pipelines

⸻

Key Takeaway

Pub/Sub enables scalable, reliable, and asynchronous communication between distributed systems.

