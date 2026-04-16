import base64
import os

from django.db import models
from django.utils import timezone


class DataSource(models.Model):
    class Priority(models.IntegerChoices):
        PRIMARY = 1, "Principal"
        FALLBACK = 2, "Fallback"
        TERTIARY = 3, "Tertiaire"

    name = models.CharField(max_length=100, unique=True)
    _api_key = models.TextField(db_column="api_key", blank=True, default="")
    base_url = models.CharField(max_length=500, blank=True, default="")
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.PRIMARY)
    rate_limit_per_minute = models.IntegerField(default=60)
    rate_limit_per_day = models.IntegerField(default=500)
    requests_today = models.IntegerField(default=0)
    last_reset = models.DateTimeField(default=timezone.now)
    is_healthy = models.BooleanField(default=True)
    consecutive_errors = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["priority", "name"]

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        health = "healthy" if self.is_healthy else "unhealthy"
        return f"{self.name} (P{self.priority}, {status}, {health})"

    @property
    def api_key(self) -> str:
        if not self._api_key:
            return ""
        try:
            return base64.b64decode(self._api_key.encode()).decode()
        except Exception:
            return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        if value:
            self._api_key = base64.b64encode(value.encode()).decode()
        else:
            self._api_key = ""

    def increment_requests(self):
        now = timezone.now()
        if now.date() > self.last_reset.date():
            self.requests_today = 0
            self.last_reset = now
        self.requests_today += 1
        self.save(update_fields=["requests_today", "last_reset", "updated_at"])

    def reset_counter(self):
        self.requests_today = 0
        self.last_reset = timezone.now()
        self.save(update_fields=["requests_today", "last_reset", "updated_at"])

    def mark_healthy(self):
        self.is_healthy = True
        self.consecutive_errors = 0
        self.save(update_fields=["is_healthy", "consecutive_errors", "updated_at"])

    def record_error(self):
        self.consecutive_errors += 1
        if self.consecutive_errors >= 3:
            self.is_healthy = False
        self.save(update_fields=["is_healthy", "consecutive_errors", "updated_at"])

    @property
    def quota_exceeded(self) -> bool:
        return self.requests_today >= self.rate_limit_per_day
