from django.contrib import admin

from .models import Notification, ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "consumer", "service_type", "barangay", "status", "preferred_date", "created_at"]
    list_filter = ["service_type", "status", "barangay"]
    search_fields = ["consumer__username", "barangay", "address"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["user__username", "message"]
