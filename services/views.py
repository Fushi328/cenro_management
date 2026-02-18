from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
import uuid
import json
import time

from accounts.decorators import role_required
from accounts.models import User
from scheduling.models import Schedule

from .forms import ServiceRequestForm, ServiceRequestStep1Form, ServiceRequestStep2Form, ServiceRequestStep3Form, ServiceRequestStep4Form
from .location import detect_barangay_for_point
from .geocode import address_in_bayawan, extract_barangay, reverse_geocode_osm
from .models import Notification, ServiceRequest


@login_required
@role_required("CONSUMER")
def create_request(request):
    """Multi-step service request form"""
    step = request.GET.get("step", 1)
    
    try:
        step = int(step)
    except ValueError:
        step = 1
    
    # Initialize session for multi-step form
    if "service_request_data" not in request.session:
        request.session["service_request_data"] = {}
    
    form_data = request.session.get("service_request_data", {})
    
    # Handle form submission
    if request.method == "POST":
        if step == 1:
            form = ServiceRequestStep1Form(request.POST)
            if form.is_valid():
                form_data.update({
                    "first_name": form.cleaned_data["first_name"],
                    "last_name": form.cleaned_data["last_name"],
                    "mobile_number": form.cleaned_data["mobile_number"],
                })
                request.session["service_request_data"] = form_data
                return HttpResponseRedirect(reverse("services:create_request") + "?step=2")
        
        elif step == 2:
            form = ServiceRequestStep2Form(request.POST)
            if form.is_valid():
                form_data.update({
                    # Barangay is always auto-detected server-side from GPS point.
                    "barangay": form.cleaned_data["barangay"],
                    "address": form.cleaned_data.get("address") or "",
                    "gps_latitude": form.cleaned_data.get("gps_latitude"),
                    "gps_longitude": form.cleaned_data.get("gps_longitude"),
                })
                request.session["service_request_data"] = form_data
                return HttpResponseRedirect(reverse("services:create_request") + "?step=3")
        
        elif step == 3:
            form = ServiceRequestStep3Form(request.POST, request.FILES)
            if form.is_valid():
                form_data.update({
                    "service_type": form.cleaned_data["service_type"],
                    "preferred_date": str(form.cleaned_data["preferred_date"]),
                })
                if form.cleaned_data.get("bawad_receipt"):
                    request.session["bawad_receipt"] = form.cleaned_data.get("bawad_receipt")
                request.session["service_request_data"] = form_data
                return HttpResponseRedirect(reverse("services:create_request") + "?step=4")
        
        elif step == 4:
            form = ServiceRequestStep4Form(request.POST)
            if form.is_valid() and form_data:
                # Create the service request
                from datetime import datetime
                from decimal import Decimal
                
                # Convert GPS coordinates from string to Decimal
                gps_latitude = None
                gps_longitude = None
                
                if form_data.get("gps_latitude"):
                    try:
                        gps_latitude = Decimal(str(form_data.get("gps_latitude")))
                    except (ValueError, TypeError):
                        pass
                
                if form_data.get("gps_longitude"):
                    try:
                        gps_longitude = Decimal(str(form_data.get("gps_longitude")))
                    except (ValueError, TypeError):
                        pass
                
                service_request = ServiceRequest.objects.create(
                    consumer=request.user,
                    barangay=form_data.get("barangay"),
                    address=form_data.get("address"),
                    service_type=form_data.get("service_type", "DECLOGGING"),
                    preferred_date=datetime.strptime(form_data.get("preferred_date"), "%Y-%m-%d").date(),
                    preferred_time=timezone.now().time(),
                    gps_latitude=gps_latitude,
                    gps_longitude=gps_longitude,
                )
                
                Notification.objects.create(
                    user=request.user,
                    message=f"Your {service_request.get_service_type_display()} request has been submitted.",
                )
                
                # Generate reference number
                reference_number = f"ECO-{timezone.now().year}-{service_request.id % 1000:03d}"
                
                # Clear session
                del request.session["service_request_data"]
                
                messages.success(request, "Service request submitted successfully!")
                return render(request, "services/request_success.html", {
                    "reference_number": reference_number,
                    "service_request": service_request
                })
    
    # Prepare form based on step
    if step == 1:
        form = ServiceRequestStep1Form(initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        })
    elif step == 2:
        form = ServiceRequestStep2Form(initial=form_data)
    elif step == 3:
        form = ServiceRequestStep3Form(initial=form_data)
    elif step == 4:
        form = ServiceRequestStep4Form()
    else:
        form = ServiceRequestStep1Form()
        step = 1
    
    context = {
        "form": form,
        "step": step,
        "form_data": form_data,
    }
    
    return render(request, "services/create_request_wizard.html", context)


_RG_CACHE: dict[str, tuple[float, dict]] = {}
_RG_CACHE_TTL_SECONDS = 60 * 10


def _rg_cache_get(key: str):
    now = time.time()
    item = _RG_CACHE.get(key)
    if not item:
        return None
    ts, val = item
    if now - ts > _RG_CACHE_TTL_SECONDS:
        _RG_CACHE.pop(key, None)
        return None
    return val


def _rg_cache_set(key: str, val: dict):
    _RG_CACHE[key] = (time.time(), val)


@login_required
def reverse_geocode(request):
    """
    Reverse geocode (lat, lon) via OSM Nominatim.
    We proxy this server-side to set a proper User-Agent and avoid browser CORS issues.
    """
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    if not lat or not lon:
        return JsonResponse({"ok": False, "error": "Missing lat/lon"}, status=400)

    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid lat/lon"}, status=400)

    detected = detect_barangay_for_point(lat_f, lon_f)

    cache_key = f"{round(lat_f, 6)},{round(lon_f, 6)}"
    cached = _rg_cache_get(cache_key)
    if cached:
        cached["barangay"] = detected or cached.get("barangay")
        cached["within_bayawan"] = bool(detected) or bool(cached.get("within_bayawan"))
        return JsonResponse(cached)

    data = reverse_geocode_osm(lat_f, lon_f)
    if not data:
        return JsonResponse({"ok": False, "error": "Reverse geocoding failed"}, status=502)

    address = data.get("address") or {}
    display_name = data.get("display_name")

    within_bayawan = bool(detected) or address_in_bayawan(address, display_name)
    barangay = detected or extract_barangay(address)

    payload = {
        "ok": True,
        "within_bayawan": within_bayawan,
        "barangay": barangay,  # GeoJSON result preferred; fallback to OSM when available
        "display_name": display_name,
        "address": address,
    }
    _rg_cache_set(cache_key, payload)
    return JsonResponse(payload)


@login_required
def request_list(request):
    if request.user.is_admin():
        requests = ServiceRequest.objects.all().select_related("consumer").order_by("-created_at")
    elif request.user.is_staff_member():
        requests = ServiceRequest.objects.filter(
            schedule__assigned_staff=request.user
        ).select_related("consumer").order_by("-created_at")
    else:
        requests = ServiceRequest.objects.filter(consumer=request.user).order_by("-created_at")
    return render(request, "services/request_list.html", {"requests": requests})


@login_required
def request_detail(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    if not request.user.is_admin() and service_request.consumer != request.user:
        messages.error(request, "You do not have permission to view this request.")
        return redirect("services:request_list")
    return render(request, "services/request_detail.html", {"request": service_request})


@login_required
def history(request):
    if request.user.is_admin():
        requests = ServiceRequest.objects.all().select_related("consumer").order_by("-created_at")
    else:
        requests = ServiceRequest.objects.filter(consumer=request.user).order_by("-created_at")
    return render(request, "services/history.html", {"requests": requests})


@login_required
@role_required("ADMIN")
def client_records(request):
    search = request.GET.get("search", "")
    barangay_filter = request.GET.get("barangay", "")
    consumers = User.objects.filter(role=User.Role.CONSUMER).select_related("consumer_profile").prefetch_related("service_requests")
    if search:
        consumers = consumers.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(username__icontains=search)
        )
    if barangay_filter:
        consumers = consumers.filter(consumer_profile__barangay=barangay_filter)
    barangays = User.objects.filter(role=User.Role.CONSUMER).values_list(
        "consumer_profile__barangay", flat=True
    ).distinct()
    # Compute last and next declogging for each consumer
    consumer_data = []
    for consumer in consumers:
        last_declogging = (
            ServiceRequest.objects.filter(
                consumer=consumer,
                service_type=ServiceRequest.ServiceType.DECLOGGING,
                status=ServiceRequest.Status.COMPLETED
            )
            .order_by("-preferred_date")
            .first()
        )
        next_declogging = None
        if last_declogging:
            from datetime import timedelta
            next_declogging = last_declogging.preferred_date + timedelta(days=4 * 365)
        consumer_data.append({
            "consumer": consumer,
            "last_declogging": last_declogging.preferred_date if last_declogging else None,
            "next_declogging": next_declogging,
        })
    context = {"consumer_data": consumer_data, "barangays": barangays}
    return render(request, "services/client_records.html", context)


@login_required
@role_required("ADMIN")
def compute_fee(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == "POST":
        fee_amount = request.POST.get("fee_amount")
        fee_notes = request.POST.get("fee_notes", "")
        if fee_amount:
            service_request.fee_amount = fee_amount
            service_request.fee_notes = fee_notes
            service_request.save()
            Notification.objects.create(
                user=service_request.consumer,
                message=f"Fee computed for your {service_request.get_service_type_display()} request: ₱{fee_amount}",
            )
            messages.success(request, "Fee computed successfully.")
        return redirect("services:request_detail", pk=pk)
    return render(request, "services/compute_fee.html", {"request": service_request})


@login_required
@role_required("ADMIN")
def confirm_payment(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == "POST":
        receipt = request.FILES.get("treasurer_receipt")
        if receipt:
            service_request.treasurer_receipt = receipt
            service_request.payment_confirmed_at = timezone.now()
            service_request.save()
            Notification.objects.create(
                user=service_request.consumer,
                message=f"Payment confirmed for your {service_request.get_service_type_display()} request.",
            )
            messages.success(request, "Payment confirmed successfully.")
        return redirect("services:request_detail", pk=pk)
    return render(request, "services/confirm_payment.html", {"request": service_request})


@login_required
@role_required("ADMIN", "STAFF")
def complete_request(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    if request.user.is_staff_member() and service_request.schedule.assigned_staff != request.user:
        messages.error(request, "You can only complete requests assigned to you.")
        return redirect("services:request_list")
    service_request.status = ServiceRequest.Status.COMPLETED
    service_request.save()
    Notification.objects.create(
        user=service_request.consumer,
        message=f"Your {service_request.get_service_type_display()} request has been completed.",
    )
    messages.success(request, "Request marked as completed.")
    return redirect("services:request_detail", pk=pk)
