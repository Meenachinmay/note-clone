from src.domain.health_check_service import HealthCheckService

class HealthCheckHandler:
    def __init__(self):
        self.service = HealthCheckService()

    def handle(self):
        return self.service.check_health()
