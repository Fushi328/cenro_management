from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User
from services.models import ServiceRequest

from .models import Schedule


@login_required
def schedule_list(request):
    if request.user.is_admin():
        schedules = Schedule.objects.all().select_related("service_request", "assigned_staff").order_by("service_date")
    elif request.user.is_staff_member():
        schedules = Schedule.objects.filter(assigned_staff=request.user).select_related(
            "service_request"
        ).order_by("service_date")
    else:
        schedules = Schedule.objects.filter(service_request__consumer=request.user).select_related(
            "service_request", "assigned_staff"
        ).order_by("service_date")
    return render(request, "scheduling/schedule_list.html", {"schedules": schedules})


@login_required
@role_required("ADMIN")
def create_schedule(request, request_id):
    service_request = get_object_or_404(ServiceRequest, pk=request_id)
    if request.method == "POST":
        barangay = request.POST.get("barangay")
        service_date = request.POST.get("service_date")
        service_time = request.POST.get("service_time")
        if barangay and service_date and service_time:
            schedule, created = Schedule.objects.get_or_create(
                service_request=service_request,
                defaults={
                    "barangay": barangay,
                    "service_date": service_date,
                    "service_time": service_time,
                },
            )
            if created:
                messages.success(request, "Schedule created successfully.")
            else:
                messages.info(request, "Schedule already exists for this request.")
            return redirect("scheduling:schedule_list")
    return render(request, "scheduling/create_schedule.html", {"request": service_request})


@login_required
@role_required("ADMIN")
def assign_staff(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    staff_members = User.objects.filter(role=User.Role.STAFF, is_approved=True)
    if request.method == "POST":
        staff_id = request.POST.get("staff_id")
        if staff_id:
            staff = get_object_or_404(User, pk=staff_id, role=User.Role.STAFF)
            schedule.assigned_staff = staff
            schedule.save()
            messages.success(request, f"Staff {staff.get_full_name()} assigned successfully.")
            return redirect("scheduling:schedule_list")
    return render(request, "scheduling/assign_staff.html", {"schedule": schedule, "staff_members": staff_members})
