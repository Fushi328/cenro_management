from django.contrib import admin

from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ["service_request", "barangay", "service_date", "service_time", "assigned_staff"]
    list_filter = ["barangay", "service_date"]
    search_fields = ["service_request__consumer__username", "barangay"]
