from root_agent import onboard_supplier
from negotiate_rfq import negotiate_rfq_handler

def onboard_supplier_http(request):
    payload = request.get_json(silent=True)
    return onboard_supplier(payload)

def negotiate_rfq_http(request):
    payload = request.get_json(silent=True)
    return negotiate_rfq_handler(payload)
