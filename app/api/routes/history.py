from flask import Blueprint, request, jsonify
from app.db import get_db
from app.models import HealthCheck
from datetime import datetime, timezone, timedelta
from sqlalchemy import desc

history_bp = Blueprint("history", __name__, url_prefix="/api/v1")

@history_bp.route("/history", methods=['GET'])
def get_check_history():
    """
    Return the health check history.
    Query params
        - url: The URL to health check
        - hours: Get checks from the last N hours (defaults to 24)
        - limit: Maximum number of results (default 100, max 1000)
    """
    
    db_session = get_db()
    try:
        query = db_session.query(HealthCheck)
        
        url = request.args.get("url", "")
        if url:
            query = query.filter(HealthCheck.url == url)
        
        hours = request.args.get("hours", 24, type=int)
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        if since:
            query = query.filter(HealthCheck.created_at >= since)

        limit = min(request.args.get("limit", 100, type=int), 1000)
        
        checks = query.order_by(desc(HealthCheck.created_at)).limit(limit).all()

        return jsonify({
            "count": len(checks),
            "filters": {
                "url": url,
                "hours": hours,
                "limit": limit,
            },
            "checks": [check.to_dict() for check in checks]
        })

    finally:
        db_session.close()
