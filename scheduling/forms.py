from django import forms

from .models import Schedule


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ["barangay", "service_date", "service_time"]
        widgets = {
            "barangay": forms.TextInput(attrs={"class": "form-control"}),
            "service_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "service_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
        }
