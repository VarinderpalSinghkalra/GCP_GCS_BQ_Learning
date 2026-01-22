def send_email(recipients, subject, body):
    """
    Sends email notification.
    SAFE: never raises exception.
    """

    if not recipients:
        print("[INFO] No email recipients, skipping email.")
        return

    try:
        # 🔕 POC MODE – NO REAL EMAIL
        print("----- EMAIL (POC MODE) -----")
        print("To:", recipients)
        print("Subject:", subject)
        print("Body:", body)
        print("----------------------------")

    except Exception as e:
        print(f"[WARN] Email send failed: {e}")

