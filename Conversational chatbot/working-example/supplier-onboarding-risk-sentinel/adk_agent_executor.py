def execute_agent(agent, payload: dict) -> dict:
    """
    POC-safe agent executor.
    Deterministic logic for stability + demos.
    """

    agent_name = getattr(agent, "name", "").lower()

    # -----------------------------
    # Document collection
    # -----------------------------
    if "document" in agent_name:
        return {"documents": ["W-9", "W-8"]}

    # -----------------------------
    # Document validation
    # -----------------------------
    if "validation" in agent_name:
        return {"valid": True}

    # -----------------------------
    # Compliance
    # -----------------------------
    if "compliance" in agent_name:
        return {"compliant": True}

    # -----------------------------
    # Risk scoring (UPDATED LOGIC)
    # -----------------------------
    if "risk" in agent_name:
        country = payload.get("country", "").upper()
        supplier = payload.get("supplier_name", "").lower()

        # HIGH risk – sanctioned countries
        if country in ["IR", "KP", "RU"]:
            return {
                "risk_score": 90,
                "risk_reason": "Sanctioned country"
            }

        # MEDIUM risk – large global firms
        high_profile = [
            "accenture", "deloitte", "pwc",
            "ey", "kpmg", "ibm", "oracle"
        ]
        if any(name in supplier for name in high_profile):
            return {
                "risk_score": 50,
                "risk_reason": "High-profile global supplier"
            }

        # MEDIUM risk – non-US supplier
        if country and country != "US":
            return {
                "risk_score": 40,
                "risk_reason": "Non-US supplier"
            }

        # LOW risk – default
        return {
            "risk_score": 20,
            "risk_reason": "Domestic low-risk supplier"
        }

    # -----------------------------
    # Legal review
    # -----------------------------
    if "legal" in agent_name:
        return {"review": "No legal issues identified"}

    # -----------------------------
    # Notification
    # -----------------------------
    if "notification" in agent_name:
        return {
            "recipients": ["procurement@example.com"],
            "subject": "Supplier Onboarding Decision",
            "body": "Supplier onboarding completed."
        }

    return {}

