
=====================================================
PROJECT: Case Management Dashboard Architecture
=====================================================

OVERVIEW:
This system integrates Salesforce (conceptual), AppSheet, and Google Chat
to provide a no-backend case management solution with real-time notifications.

-----------------------------------------------------
END-TO-END FLOW
-----------------------------------------------------

1. Customer sends email
2. Salesforce Email-to-Case creates a Case
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

Salesforce (Email-to-Case)
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
   - Salesforce
   - Handles case creation and lifecycle

2. DATA LAYER:
   - Google Sheets
   - Stores structured case data

3. APPLICATION LAYER:
   - AppSheet
   - Dashboard (Table, Charts, KPI)
   - Automation (Bots, Conditions)

4. NOTIFICATION LAYER:
   - Google Chat
   - Receives webhook alerts

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
- Easy integration and deployment

-----------------------------------------------------
LIMITATIONS
-----------------------------------------------------

- No direct Salesforce-AppSheet integration
- Depends on Google Sheets sync
- Limited error handling
- Not fully real-time

-----------------------------------------------------
FUTURE ENHANCEMENTS
-----------------------------------------------------

- Add GCP Cloud Functions (middleware)
- Replace Sheets with Cloud SQL / BigQuery
- Add retry & logging mechanism
- Implement AI-based prioritization

-----------------------------------------------------
FINAL ARCHITECTURE SUMMARY
-----------------------------------------------------

Salesforce → Google Sheets → AppSheet → Google Chat

=====================================================