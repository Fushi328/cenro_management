from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class ServiceRequest(models.Model):
    class ServiceType(models.TextChoices):
        DECLOGGING = "DECLOGGING", "Septage Declogging"
        GRASS_CUTTING = "GRASS_CUTTING", "Grass Cutting"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"

    consumer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="service_requests")
    barangay = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    bawad_receipt = models.FileField(upload_to="bawad_receipts/", null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # GPS Coordinates for location picker
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Computed by admin
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fee_notes = models.CharField(max_length=255, blank=True)

    # Treasurer payment confirmation
    treasurer_receipt = models.FileField(upload_to="treasurer_receipts/", null=True, blank=True)
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)
    
    # Cubic meters for declogging services
    cubic_meters = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)

    def __str__(self) -> str:
        return f"{self.get_service_type_display()} - {self.consumer} ({self.barangay})"

    @property
    def is_within_4_year_cycle(self) -> bool:
        if self.service_type != self.ServiceType.DECLOGGING:
            return True
        # Check if there was a completed declogging in the last 4 years
        four_years_ago = timezone.now().date() - timedelta(days=4 * 365)
        return not ServiceRequest.objects.filter(
            consumer=self.consumer,
            service_type=self.ServiceType.DECLOGGING,
            status=self.Status.COMPLETED,
            preferred_date__gte=four_years_ago,
        ).exists()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Notification for {self.user}: {self.message[:50]}"

