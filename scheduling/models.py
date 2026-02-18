from __future__ import annotations

from django.conf import settings
from django.db import models

from services.models import ServiceRequest

User = settings.AUTH_USER_MODEL


class Schedule(models.Model):
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="schedule",
    )
    barangay = models.CharField(max_length=255)
    service_date = models.DateField()
    service_time = models.TimeField()
    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_schedules",
        limit_choices_to={"role": "STAFF"},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.service_request} on {self.service_date}"

