from __future__ import annotations

import math
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class ConfigurableRate(models.Model):
    """Admin-editable billing constants."""

    key = models.CharField(max_length=80, unique=True)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)

    DEFAULTS = {
        "residential_trucking_within": (Decimal("2160"), "Fixed trucking - Residential within Bayawan"),
        "commercial_trucking_within": (Decimal("2376"), "Fixed trucking - Commercial within Bayawan"),
        "outside_trucking": (Decimal("3000"), "Fixed trucking - Outside Bayawan City"),
        "desludging_per_m3": (Decimal("500"), "Desludging fee per cubic meter"),
        "second_trip_surcharge": (Decimal("360"), "Additional surcharge per m3 on 2nd+ trip"),
        "meals_per_head": (Decimal("200"), "Meals & transportation allowance per person"),
        "inspection_fee": (Decimal("150"), "Inspection fee"),
        "per_km_rate": (Decimal("20"), "Rate per km beyond free distance"),
        "free_km": (Decimal("20"), "Free trucking distance from CENRO office (km)"),
        "wear_tear_pct": (Decimal("20"), "Wear and tear percentage (outside only)"),
        "bawad_free_limit_m3": (Decimal("5"), "BAWAD free service limit (cubic meters)"),
        "bawad_cycle_years": (Decimal("4"), "BAWAD cycle period (years)"),
        "min_cubic_meters": (Decimal("5"), "Minimum billable cubic meters"),
    }

    class Meta:
        verbose_name = "Configurable Rate"
        verbose_name_plural = "Configurable Rates"

    def __str__(self) -> str:
        return f"{self.key} = {self.value}"

    @classmethod
    def get(cls, key: str, default=None) -> Decimal:
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            if key in cls.DEFAULTS:
                return cls.DEFAULTS[key][0]
            if default is not None:
                return Decimal(str(default))
            return Decimal("0")

    @classmethod
    def seed_defaults(cls):
        for key, (value, description) in cls.DEFAULTS.items():
            cls.objects.get_or_create(key=key, defaults={"value": value, "description": description})


class ChargeCategory(models.Model):
    """Categories for service charges"""

    class Category(models.TextChoices):
        RESIDENTIAL = "RESIDENTIAL", "Residential"
        COMMERCIAL = "COMMERCIAL", "Commercial"

    category = models.CharField(max_length=20, choices=Category.choices, unique=True)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base rate per cubic meter or unit")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Charge Categories"

    def __str__(self) -> str:
        return f"{self.get_category_display()} - ₱{self.base_rate}"


class ServiceComputation(models.Model):
    """Detailed computation and charges for a service request"""

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FREE = "FREE", "Free (BAWAD)"

    service_request = models.OneToOneField(
        "services.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="computation",
    )
    charge_category = models.ForeignKey(
        ChargeCategory, on_delete=models.SET_NULL, null=True, blank=True
    )

    is_outside_bayawan = models.BooleanField(default=False)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    cubic_meters = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    trips = models.PositiveIntegerField(default=1)
    personnel_count = models.PositiveIntegerField(default=4)

    fixed_trucking = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desludging_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    distance_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wear_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    meals_transport_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inspection_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    prepared_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="computations_prepared"
    )
    receipt_generated = models.BooleanField(default=False)
    receipt_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Computation for {self.service_request} - ₱{self.total_charge}"

    def get_desludging_breakdown(self):
        """Return a list of {label, amount} for detailed desludging fee breakdown.
        Trip 1: max 5 m³ × base rate. Trip 2+: remaining volume × (base + ₱360 surcharge).
        """
        R = ConfigurableRate.get
        desludging_per_m3 = R("desludging_per_m3")
        second_trip_surcharge = R("second_trip_surcharge")
        min_m3 = R("min_cubic_meters")
        max_m3_per_trip = Decimal("5")
        effective_m3 = max(self.cubic_meters, min_m3)
        rate_extra = desludging_per_m3 + second_trip_surcharge
        lines = []
        for t in range(self.trips):
            if t == 0:
                vol_this_trip = max_m3_per_trip  # First trip always 5 m³ (min and max)
            else:
                remaining = effective_m3 - (t * max_m3_per_trip)
                vol_this_trip = min(max_m3_per_trip, max(Decimal("0"), remaining))
            if vol_this_trip <= 0:
                continue
            rate = desludging_per_m3 if t == 0 else rate_extra
            amt = vol_this_trip * rate
            if t == 0:
                lines.append({
                    "label": f"Trip 1: 5 m³ × ₱{desludging_per_m3}/m³ (min 5 m³, max 5 m³)",
                    "amount": amt,
                })
            else:
                lines.append({
                    "label": f"Trip {t + 1}: {vol_this_trip} m³ × ₱{rate_extra}/m³ (₱{desludging_per_m3} + ₱{second_trip_surcharge} surcharge)",
                    "amount": amt,
                })
        return lines

    def calculate_charges(self):
        """Calculate all charges based on the correct business rules."""
        from services.models import ServiceRequest

        sr = self.service_request
        R = ConfigurableRate.get

        desludging_per_m3 = R("desludging_per_m3")
        second_trip_surcharge = R("second_trip_surcharge")
        meals_per_head = R("meals_per_head")
        inspection_fee = R("inspection_fee")
        per_km_rate = R("per_km_rate")
        free_km = R("free_km")
        wear_pct = R("wear_tear_pct") / Decimal("100")
        min_m3 = R("min_cubic_meters")

        effective_m3 = max(self.cubic_meters, min_m3)

        # 1 trip = max 5 m³; more than 5 m³ auto-adjusts to additional trips
        max_m3_per_trip = Decimal("5")
        self.trips = max(1, math.ceil(float(self.cubic_meters) / float(max_m3_per_trip)))

        # Fixed trucking based on service type and location
        if self.is_outside_bayawan:
            self.fixed_trucking = R("outside_trucking")
        elif sr.service_type == ServiceRequest.ServiceType.COMMERCIAL_DESLUDGING:
            self.fixed_trucking = R("commercial_trucking_within")
        else:
            self.fixed_trucking = R("residential_trucking_within")

        # Desludging fee: Trip 1 = always 5 m³ × 500/m³; Trip 2+ = remaining m³ × 860/m³
        self.desludging_fee = Decimal("0")
        for t in range(self.trips):
            if t == 0:
                vol_this_trip = max_m3_per_trip  # First trip always 5 m³ (min and max)
            else:
                remaining = effective_m3 - (t * max_m3_per_trip)
                vol_this_trip = min(max_m3_per_trip, max(Decimal("0"), remaining))
            rate = desludging_per_m3 if t == 0 else (desludging_per_m3 + second_trip_surcharge)
            self.desludging_fee += vol_this_trip * rate

        # Distance charge: excess beyond free_km
        dist = self.distance_km or Decimal("0")
        excess_km = max(Decimal("0"), dist - free_km)
        self.distance_charge = excess_km * per_km_rate * 2

        # Meals and transportation
        self.meals_transport_charge = self.personnel_count * meals_per_head

        # Inspection
        self.inspection_charge = inspection_fee

        # Wear and tear (outside Bayawan only)
        if self.is_outside_bayawan:
            base_for_wear = R("outside_trucking") + self.distance_charge + (effective_m3 * desludging_per_m3)
            self.wear_charge = base_for_wear * wear_pct
        else:
            self.wear_charge = Decimal("0")

        # Total
        self.total_charge = (
            self.fixed_trucking
            + self.desludging_fee
            + self.distance_charge
            + self.wear_charge
            + self.meals_transport_charge
            + self.inspection_charge
        )

        # BAWAD discount
        if sr.connected_to_bawad and sr.bawad_free_eligible:
            self.total_charge = Decimal("0")
            self.payment_status = self.PaymentStatus.FREE

    def save(self, *args, **kwargs):
        self.calculate_charges()
        super().save(*args, **kwargs)


class DecloggingApplication(models.Model):
    """Declogging application with signatures"""

    service_request = models.OneToOneField(
        "services.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="declogging_app",
    )
    applicant_name = models.CharField(max_length=255)
    applicant_signature = models.FileField(upload_to="signatures/", null=True, blank=True)
    applicant_sign_date = models.DateField(null=True, blank=True)

    cenro_representative = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="declogging_apps_signed",
    )
    cenro_signature = models.FileField(upload_to="signatures/", null=True, blank=True)
    cenro_sign_date = models.DateField(null=True, blank=True)

    application_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_signed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Declogging App - {self.applicant_name}"


class MembershipRecord(models.Model):
    """Track membership with service history and balance"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="membership_record")
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_free = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Membership - {self.user.get_full_name()}"
