from django import forms

from .models import ServiceRequest
from .geocode import address_in_bayawan, extract_barangay, reverse_geocode_osm
from .location import detect_barangay_for_point, nearest_barangay, within_service_bounds


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ["barangay", "address", "service_type", "preferred_date", "preferred_time", "bawad_receipt", "notes"]
        widgets = {
            "barangay": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "service_type": forms.Select(attrs={"class": "form-control"}),
            "preferred_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "bawad_receipt": forms.FileInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ServiceRequestStep1Form(forms.Form):
    """Personal Information Step"""
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"})
    )
    mobile_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Mobile number"})
    )


class ServiceRequestStep2Form(forms.Form):
    """Location Step"""

    # Auto-filled by GeoJSON point-in-polygon (no manual selection).
    barangay = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
        help_text="Auto-detected from the pin location.",
    )

    # Optional: user can refine landmark/house no. Reverse geocode may prefill.
    address = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "House number, Street name, near [Landmark] (optional)",
            }
        ),
    )
    gps_latitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )
    gps_longitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("gps_latitude")
        lon = cleaned.get("gps_longitude")
        if lat is None or lon is None:
            raise forms.ValidationError("Please select your location on the map.")

        lat_f = float(lat)
        lon_f = float(lon)
        detected = detect_barangay_for_point(lat_f, lon_f)
        if not detected:
            data = reverse_geocode_osm(lat_f, lon_f)
            if data:
                address = data.get("address") or {}
                display_name = data.get("display_name")
                within = address_in_bayawan(address, display_name)
                if within:
                    detected = extract_barangay(address) or nearest_barangay(lat_f, lon_f)
            if not detected and within_service_bounds(lat_f, lon_f):
                detected = nearest_barangay(lat_f, lon_f)
            if not detected:
                raise forms.ValidationError(
                    "Selected location is outside Bayawan City. Please move the pin inside the city boundary."
                )

        cleaned["barangay"] = detected
        return cleaned


class ServiceRequestStep3Form(forms.Form):
    """Service Details Step"""
    SERVICE_CHOICES = [
        ("", "Select service type"),
        ("DECLOGGING", "Septage Desludging (Residential)"),
        ("COMMERCIAL_DECLOGGING", "Septage Desludging (Commercial)"),
        ("GRASS_CUTTING", "Grass Cutting Service"),
    ]
    
    service_type = forms.ChoiceField(
        choices=SERVICE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    preferred_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date"
        }),
        help_text="Final schedule is subject to truck availability."
    )
    bawad_receipt = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"})
    )


class ServiceRequestStep4Form(forms.Form):
    """Confirmation Step"""
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="I confirm that the information provided is correct."
    )
