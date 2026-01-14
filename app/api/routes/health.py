from flask import Blueprint, jsonify, current_app
from datetime import datetime, timezone
from app.db import get_db
from sqlalchemy import text

health_bp = Blueprint("health", __name__)

@health_bp.route('/health', methods=['GET'])
def app_health():
    """Check the health of the monitoring service."""
    db_status = "connected"
    db_session = get_db()
    try:
        db_session.execute(text("SELECT 1"))

    except Exception as e:
        db_status = "failed"
    finally:
        db_session.close()
        
    return jsonify({
        "service": "thatworks-monitor",
        "version": current_app.config['SERVICE_VERSION'],
        "status": "healthy",
        "db_status": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
