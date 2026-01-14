from .health import health_bp
from .check import checks_bp
from .history import history_bp
from .monitored import monitored_bp

__all__ = ['health_bp', 'checks_bp', 'history_bp', 'monitored_bp']
