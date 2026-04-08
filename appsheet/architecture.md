=====================================================
PROJECT: Case Management Dashboard Architecture
=====================================================

OVERVIEW:
This system integrates a Buying Hub (external system), Salesforce,
AppSheet, and Google Chat to provide a no-backend case management
solution with real-time notifications and dashboard visibility.

-----------------------------------------------------
END-TO-END FLOW
-----------------------------------------------------

1. Buying Hub system sends case data
2. Salesforce receives data and creates Case records
3. Case data is stored in Google Sheets (data layer)
4. AppSheet reads and syncs case data
5. Dashboard updates with latest case information
6. AppSheet Bot monitors data changes
7. On trigger, webhook is executed
8. Notification sent to Google Chat
9. User receives alert and opens dashboard

-----------------------------------------------------
ARCHITECTURE FLOW (LINEAR)
-----------------------------------------------------

Buying Hub System
        ↓
Salesforce (Case Creation)
        ↓
Case Object
        ↓
Google Sheets (Data Layer)
        ↓
AppSheet (Dashboard + Automation)
        ↓
Webhook Trigger
        ↓
Google Chat (Notification)
        ↓
User Action (View Dashboard)

-----------------------------------------------------
SYSTEM COMPONENTS
-----------------------------------------------------

1. SOURCE SYSTEM:
   - Buying Hub System
   - Sends structured case data to Salesforce

2. CRM LAYER:
   - Salesforce
   - Handles case creation and lifecycle management

3. DATA LAYER:
   - Google Sheets
   - Stores structured case data
   - Acts as integration bridge

4. APPLICATION LAYER:
   - AppSheet
   - Dashboard (Table, Charts, KPI)
   - Automation (Bots, Conditions)
   - Business logic (Pending count, filters)

5. NOTIFICATION LAYER:
   - Google Chat
   - Receives webhook alerts
   - Enables real-time team communication

-----------------------------------------------------
AUTOMATION LOGIC
-----------------------------------------------------

Trigger:
- Case Added or Updated

Condition:
- Status is not Closed

Action:
- Send Webhook to Google Chat

-----------------------------------------------------
SAMPLE DATA FIELDS
-----------------------------------------------------

- CaseNumber
- CaseOwner
- Status
- CreatedDate
- AgreementID
- L1Category
- L2Category

-----------------------------------------------------
KEY FEATURES
-----------------------------------------------------

- Real-time dashboard visualization
- Automated notifications via webhook
- Pending case tracking
- No backend architecture
- Lightweight and scalable design
- Easy integration and deployment

-----------------------------------------------------
LIMITATIONS
-----------------------------------------------------

- No direct Salesforce-AppSheet integration
- Depends on Google Sheets sync
- Limited error handling and retry mechanism
- Near real-time (based on sync frequency)

-----------------------------------------------------
FUTURE ENHANCEMENTS
-----------------------------------------------------

- Add GCP Cloud Functions (middleware)
- Replace Google Sheets with Cloud SQL / BigQuery
- Implement retry & logging mechanism
- Add monitoring and alerting
- AI-based case prioritization

-----------------------------------------------------
FINAL ARCHITECTURE SUMMARY
-----------------------------------------------------

Buying Hub → Salesforce → Google Sheets → AppSheet → Google Chat

=====================================================