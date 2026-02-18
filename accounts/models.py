from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"
        CONSUMER = "CONSUMER", "Consumer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONSUMER,
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="For staff and consumer accounts that require admin approval.",
    )

    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    def is_staff_member(self) -> bool:
        return self.role == self.Role.STAFF

    def is_consumer(self) -> bool:
        return self.role == self.Role.CONSUMER


class ConsumerProfile(models.Model):
    class LocationType(models.TextChoices):
        WITHIN = "within", "Within Bayawan City"
        OUTSIDE = "outside", "Outside"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="consumer_profile")
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices,
        default=LocationType.WITHIN,
    )
    barangay = models.CharField(max_length=255, blank=True)
    municipality = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=500)
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} - {self.barangay}"

