from root_agent import onboard_supplier
from flask import jsonify

def onboard_supplier_http(request):
    """
    Cloud Functions Gen2 HTTP entry point
    """
    request_json = request.get_json(silent=True)

    if not request_json:
        return jsonify({"error": "Invalid JSON"}), 400

    result = onboard_supplier(request_json)
    return jsonify(result), 200

