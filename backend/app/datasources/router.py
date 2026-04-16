from .models import DataSource


class DataSourceError(Exception):
    pass


class DataSourceRouter:
    CIRCUIT_BREAKER_THRESHOLD = 3

    def get_active_source(self) -> DataSource:
        source = (
            DataSource.objects.filter(is_active=True, is_healthy=True)
            .order_by("priority")
            .first()
        )
        if not source:
            raise DataSourceError("Aucune source de données active et saine")
        return source

    def fallback(self, exclude_id: int | None = None) -> DataSource:
        qs = DataSource.objects.filter(is_active=True, is_healthy=True)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        source = qs.order_by("priority").first()
        if not source:
            raise DataSourceError("Aucune source de fallback disponible")
        return source

    def record_request(self, source: DataSource):
        source.increment_requests()

    def is_quota_exceeded(self, source: DataSource) -> bool:
        return source.quota_exceeded

    def record_success(self, source: DataSource):
        if source.consecutive_errors > 0:
            source.mark_healthy()

    def record_error(self, source: DataSource):
        source.record_error()

    def execute_with_fallback(self, operation):
        source = self.get_active_source()

        if self.is_quota_exceeded(source):
            source = self.fallback(exclude_id=source.id)

        try:
            self.record_request(source)
            result = operation(source)
            self.record_success(source)
            return result
        except Exception:
            self.record_error(source)
            try:
                fallback_source = self.fallback(exclude_id=source.id)
                if self.is_quota_exceeded(fallback_source):
                    raise DataSourceError("Toutes les sources ont atteint leur quota")
                self.record_request(fallback_source)
                result = operation(fallback_source)
                self.record_success(fallback_source)
                return result
            except DataSourceError:
                raise
            except Exception as e:
                self.record_error(fallback_source)
                raise DataSourceError(f"Toutes les sources ont échoué : {e}")
