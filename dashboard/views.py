from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from services.models import ServiceRequest
from scheduling.models import Schedule


def home(request):
    # Redirect unauthenticated users to login
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Redirect admins to admin dashboard
    if request.user.is_admin():
        return redirect('dashboard:admin_dashboard')
    
    # Summary cards for non-admin users
    declogging_count = ServiceRequest.objects.filter(service_type=ServiceRequest.ServiceType.DECLOGGING).count()
    grass_count = ServiceRequest.objects.filter(service_type=ServiceRequest.ServiceType.GRASS_CUTTING).count()
    pending_count = ServiceRequest.objects.filter(status=ServiceRequest.Status.PENDING).count()
    completed_count = ServiceRequest.objects.filter(status=ServiceRequest.Status.COMPLETED).count()

    # Simple calendar-like data: upcoming schedules for the next 30 days
    today = date.today()
    upcoming_schedules = (
        Schedule.objects.filter(service_date__gte=today, service_date__lte=today + timedelta(days=30))
        .select_related("service_request", "assigned_staff")
        .order_by("service_date")
    )
    # Aggregate by date for quick calendar summary
    by_date = (
        upcoming_schedules.values("service_date")
        .annotate(count=Count("id"))
        .order_by("service_date")
    )

    context = {
        "declogging_count": declogging_count,
        "grass_count": grass_count,
        "pending_count": pending_count,
        "completed_count": completed_count,
        "upcoming_schedules": upcoming_schedules,
        "calendar_counts": by_date,
    }
    return render(request, "dashboard/home.html", context)

