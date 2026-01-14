from flask import Blueprint, jsonify, current_app
from datetime import datetime, timezone

health_bp = Blueprint("health", __name__)

@health_bp.route('/health', methods=['GET'])
def app_health():
    """Check the health of the monitoring service."""
    return jsonify({
        "service": "thatworks-monitor",
        "version": current_app.config['SERVICE_VERSION'],
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
