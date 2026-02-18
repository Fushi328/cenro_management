from __future__ import annotations

from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


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
        FREE = "FREE", "Free"

    service_request = models.OneToOneField(
        'services.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='computation'
    )
    charge_category = models.ForeignKey(
        ChargeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Distance-based charges (for outside Bayawan)
    is_outside_bayawan = models.BooleanField(default=False)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Base charges
    cubic_meters = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    base_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Additional charges
    distance_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Distance × 2 × ₱20
    wear_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 20% of base
    meals_transport_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ₱500/m³
    inspection_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ₱150
    
    # Total
    total_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment details
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    prepared_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='computations_prepared'
    )
    
    # Receipt
    receipt_generated = models.BooleanField(default=False)
    receipt_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Computation for {self.service_request} - ₱{self.total_charge}"

    def calculate_charges(self):
        """Calculate all charges based on service type and parameters"""
        if self.charge_category and self.cubic_meters:
            self.base_charge = self.charge_category.base_rate * self.cubic_meters
        
        # Distance charges (outside Bayawan)
        if self.is_outside_bayawan and self.distance_km:
            self.distance_charge = self.distance_km * 2 * Decimal('20')
        
        # Wear charge (20% of base)
        self.wear_charge = self.base_charge * Decimal('0.20')
        
        # Tipping charge (₱500/m³)
        self.tipping_charge = self.cubic_meters * Decimal('500')
        
        # Inspection charge
        self.inspection_charge = Decimal('150')
        
        # Total
        self.total_charge = (
            self.base_charge +
            self.distance_charge +
            self.wear_charge +
            self.meals_transport_charge +
            self.tipping_charge +
            self.inspection_charge
        )

    def save(self, *args, **kwargs):
        self.calculate_charges()
        super().save(*args, **kwargs)


class DecloggingApplication(models.Model):
    """Declogging application with signatures"""
    service_request = models.OneToOneField(
        'services.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='declogging_app'
    )
    
    # Applicant info
    applicant_name = models.CharField(max_length=255)
    applicant_signature = models.FileField(upload_to="signatures/", null=True, blank=True)
    applicant_sign_date = models.DateField(null=True, blank=True)
    
    # CENRO representative
    cenro_representative = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='declogging_apps_signed'
    )
    cenro_signature = models.FileField(upload_to="signatures/", null=True, blank=True)
    cenro_sign_date = models.DateField(null=True, blank=True)
    
    # Document
    application_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_signed = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"Declogging App - {self.applicant_name}"


class MembershipRecord(models.Model):
    """Track membership with service history and balance"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='membership_record'
    )
    
    # Balance tracking
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_free = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Membership - {self.user.get_full_name()}"


