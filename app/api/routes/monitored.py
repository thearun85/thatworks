from flask import Blueprint, request, jsonify
from app.utils import validate_url, validate_timeout
from app.db import get_db
from app.models import MonitoredUrl
from sqlalchemy.exc import IntegrityError

monitored_bp = Blueprint("monitored", __name__, url_prefix="/api/v1/monitored")

MIN_INTERVAL_SECONDS = 60 # 1 minute
MAX_INTERVAL_SECONDS = 3600 # 1 hour

@monitored_bp.route("/urls", methods=['POST'])
def add_url():
    """
    Flask endpoint to add monitored url.
    Request json data
        - "url": The URL to check
        - "name": A short name to identify the URL
        - "check_interval": how often to fire the health check, in seconds.
        - "timeout": in seconds
        - "is_active": is this url active?
    """
    # Validate request is in application/json format
    if not request.is_json:
        return jsonify({
            "error", "JSON format expected"
        }), 400
    data = request.get_json()
    
    url = data.get("url", "").strip()
    is_valid, error =  validate_url(url)
    if not is_valid:
        return jsonify({
            "error": error
        }), 400

    name = data.get("name")
    
    check_interval_s = data.get("check_interval", "")
    if check_interval_s == "":
        return jsonify({
        "error": "Missing required field: 'check_interval'"
        }), 400
    if not isinstance(check_interval_s, (int, float)):
        return jsonify({
            "error": "Invalid check_interval format"
        }), 400

    if check_interval_s < MIN_INTERVAL_SECONDS or check_interval_s > MAX_INTERVAL_SECONDS:
        return jsonify({
            "error": f"Check interval must be between {MIN_INTERVAL_SECONDS} and {MAX_INTERVAL_SECONDS}"
        }), 400
        
    timeout_s = data.get("timeout", "")
    is_valid, error = validate_timeout(timeout_s)
    if not is_valid:
        return jsonify({
            "error": error
        }), 400

    is_active = data.get("is_active", True)

    db_session = get_db()
    try:
        mu = MonitoredUrl(
            url=url,
            name=name,
            check_interval_s=check_interval_s,
            timeout_s=timeout_s,
            is_active=is_active
        )
        db_session.add(mu)
        db_session.commit()
        db_session.refresh(mu)
        return jsonify({
            "message": f"URL {url} added to monitoring",
            "monitored": mu.to_dict(),
        }), 201
    except IntegrityError as e:
        db_session.rollback()
        return jsonify({
            "error": "URL already exists in monitoring"
        }), 409
    except Exception as e:
        db_session.rollback()
        return jsonify({
            "error": f"Database error: {str(e)}"
        }), 500
    finally:
        db_session.close()

@monitored_bp.route("/urls/<int:url_id>", methods=['GET'])
def get_url(url_id:int):
    """
    Get the monitored url details.
    Query params
        "url_id": id of the URL to fetch
    """
    db_session = get_db()
    try:
        monitored = db_session.query(MonitoredUrl).filter(MonitoredUrl.id == url_id).first()
        if not monitored:
            return jsonify({
                "error": "Monitored URL not found"
            }), 404
        return jsonify(monitored.to_dict()), 200
    finally:
        db_session.close()

@monitored_bp.route("/urls/<int:url_id>", methods=['DELETE'])
def delete_url(url_id:int):
    """
    Delete a monitored url.
    Query params
        "url_id": id of the URL
    """
    db_session = get_db()
    try:
        monitored = db_session.query(MonitoredUrl).filter(MonitoredUrl.id == url_id).first()
        if not monitored:
            return jsonify({
                "error": "Monitored URL not found"
            }), 404
        db_session.delete(monitored)
        db_session.commit()
        return jsonify({
            "message": f"URL removed from monitoring"
        }), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({
            "error": f"Database error: {str(e)}"
        }), 500
        
    finally:
        db_session.close()

@monitored_bp.route("/urls/<int:url_id>", methods=['PUT'])
def update_url(url_id:int):
    """
    Update a monitored URL details.
    Can update name, check_interval, timeout, is_active.
    Cannot update: url (delete and re-ad instead).
    Query params:
        "url_id": id of the URL to update
    Request json:
        - "name": A short name to identify the URL
        - "check_interval": how often to fire the health check, in seconds.
        - "timeout": in seconds
        - "is_active": is this url active?        
    """
    atleast_one = False
    if not request.is_json:
        return jsonify({
            "error": "JSON format expected"
        }), 400

    data = request.get_json()
    
    if "url" in data:
        atleast_one = True
        return jsonify({
            "error": "Cannot update URL. Delete and re-add instead."
        }), 400

    name = data.get("name")
    
    if "check_interval" in data:
        atleast_one = True
        if not isinstance(data.get("check_interval"), (int, float)):
            return jsonify({
                "error": "Invalid check_interval format"
            }), 400

        if data.get("check_interval") < MIN_INTERVAL_SECONDS or data.get("check_interval") > MAX_INTERVAL_SECONDS:
            return jsonify({
                "error": f"Check interval must be between {MIN_INTERVAL_SECONDS} and {MAX_INTERVAL_SECONDS}"
            }), 400
        
    if "timeout" in data:
        atleast_one = True
        is_valid, error = validate_timeout(data["timeout"])
        if not is_valid:
            return jsonify({
                "error": error
            }), 400
    if "is_active" in data:
        atleast_one = True

    if not atleast_one:
        return jsonify({
            "error": "Atleast one field must be updated"
        }), 400
    db_session = get_db()
    try:
        monitored = db_session.query(MonitoredUrl).filter(MonitoredUrl.id == url_id).first()
        if not monitored:
            return jsonify({
                "error": "Monitored URL not found"
            }), 404

        if "name" in data:
            monitored.name = data["name"]
        if "check_interval" in data:
            monitored.check_interval_s = data["check_interval"]
        if "timeout" in data:
            monitored.timeout_s = data["timeout"]
        if "is_active" in data:
            monitored.is_active = data['is_active']
        db_session.commit()
        db_session.refresh(monitored)
        return jsonify({
            "message": f"Monitored URL {monitored.url} updated",
            "monitored": monitored.to_dict(),
        }), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({
            "error": f"Database error: {str(e)}"
        }), 500
    finally:
        db_session.close()

    
