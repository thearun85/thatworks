from flask import Blueprint, request, jsonify
from app.services import check_health
from app.utils import validate_url, validate_timeout


checks_bp = Blueprint("checks", __name__, url_prefix='/api/v1')

@checks_bp.route('/check', methods=['POST'])
def get_health():
    """
    Flask endpoint to check the url health.
    Request json data
        "url" - The URL to check
        "timeout" - in seconds
    """
    # Validate request is in application/json format
    if not request.is_json:
        return jsonify({
            "error", "JSON request is required"
        }), 400
        
    data = request.get_json()

    url = data.get("url", "").strip()
    # Validate url is not missing or empty
    if url == "":
        return jsonify({
            "error": "Missing required field: 'url'"
        }), 400

    is_valid, error =  validate_url(url)
    if not is_valid:
        return jsonify({
            "error": error
        }), 400

    timeout = data.get("timeout", 10)
    is_valid, error = validate_timeout(timeout)
    if not is_valid:
        return jsonify({
            "error": error
        }), 400

    result = check_health(url, timeout)
    return jsonify(result), 200
    
        
    
