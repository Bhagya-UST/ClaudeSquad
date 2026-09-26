"""
Health check endpoints for ReturnIQ
Provides liveness and readiness probes for Kubernetes/Docker
"""

from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class HealthCheck:
    """Health check manager"""

    def __init__(self):
        self.db_healthy = False
        self.rag_healthy = False
        self.api_healthy = True

    def set_db_health(self, healthy: bool):
        self.db_healthy = healthy

    def set_rag_health(self, healthy: bool):
        self.rag_healthy = healthy

    def get_liveness_status(self) -> Dict:
        """Liveness check - is the service running?"""
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_readiness_status(self) -> Dict:
        """Readiness check - is the service ready for traffic?"""
        all_healthy = self.db_healthy and self.rag_healthy and self.api_healthy

        return {
            "status": "ready" if all_healthy else "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": "healthy" if self.db_healthy else "unhealthy",
                "rag_system": "healthy" if self.rag_healthy else "unhealthy",
                "api": "healthy" if self.api_healthy else "unhealthy",
            }
        }

# Global health check instance
health_check = HealthCheck()
