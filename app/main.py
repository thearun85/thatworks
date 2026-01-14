from flask import Flask
from datetime import datetime, timezone

def create_app():
    flask_app = Flask("thatworks-monitor")

    service_start_timestamp = datetime.now(timezone.utc)
    flask_app.config['SERVICE_VERSION'] = "0.1.0"
    flask_app.config['SERVICE_START_TIMESTAMP'] = service_start_timestamp

    from app.api.routes import health_bp, checks_bp
    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(checks_bp)

    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port="5000", debug=True)
