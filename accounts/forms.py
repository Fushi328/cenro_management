from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import ConsumerProfile, User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )


class ConsumerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
        error_messages={
            "invalid": "Please enter a valid email address (e.g. user@domain.com).",
            "required": "This field is required.",
        },
    )
    barangay = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Barangay"})
    )
    municipality = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Municipality/City"})
    )
    address = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Full address"})
    )
    location_type = forms.ChoiceField(
        choices=[
            ("within", "Within Bayawan City"),
            ("outside", "Outside"),
        ],
        required=True,
        initial="within",
        widget=forms.HiddenInput(attrs={"id": "id_location_type"}),
    )
    gps_latitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput(),
    )
    gps_longitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Username"})
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Password confirmation"})
        self.fields["password2"].error_messages["password_mismatch"] = "Passwords do not match. Please enter the same password in both fields."
        for field_name, field in self.fields.items():
            if field_name in self.errors:
                cls = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{cls} is-invalid".strip()

    def clean(self):
        cleaned_data = super().clean()
        location_type = cleaned_data.get("location_type") or "within"
        municipality = (cleaned_data.get("municipality") or "").strip()
        if location_type == "outside" and not municipality:
            self.add_error("municipality", "Municipality is required when you are outside Bayawan City.")
        elif location_type == "within":
            barangay = (cleaned_data.get("barangay") or "").strip()
            if not barangay:
                self.add_error("barangay", "Barangay is required when you are within Bayawan City.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CONSUMER
        user.is_active = True
        user.is_approved = True  # Consumers can be auto-approved; tweak if manual approval is needed.
        if commit:
            user.save()
            ConsumerProfile.objects.create(
                user=user,
                location_type=self.cleaned_data["location_type"],
                barangay=self.cleaned_data.get("barangay") or "",
                municipality=self.cleaned_data.get("municipality") or "",
                address=self.cleaned_data["address"],
                gps_latitude=self.cleaned_data.get("gps_latitude"),
                gps_longitude=self.cleaned_data.get("gps_longitude"),
            )
        return user


class StaffRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STAFF
        user.is_active = True
        user.is_approved = False  # Requires admin approval
        if commit:
            user.save()
        return user

