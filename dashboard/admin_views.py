from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import User
from services.models import ServiceRequest, Notification
from scheduling.models import Schedule


@login_required
@role_required("ADMIN")
def admin_dashboard(request):
    """Main admin dashboard with charts and statistics"""
    today = date.today()
    start_of_month = today.replace(day=1)
    
    # Summary cards
    total_requests = ServiceRequest.objects.count()
    pending_count = ServiceRequest.objects.filter(status=ServiceRequest.Status.PENDING).count()
    completed_this_month = ServiceRequest.objects.filter(
        status=ServiceRequest.Status.COMPLETED,
        preferred_date__gte=start_of_month
    ).count()
    
    # Calculate trends (comparing to last month)
    last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
    last_month_completed = ServiceRequest.objects.filter(
        status=ServiceRequest.Status.COMPLETED,
        preferred_date__gte=last_month_start,
        preferred_date__lt=start_of_month
    ).count()
    
    efficiency_change = 0
    if last_month_completed > 0:
        efficiency_change = ((completed_this_month - last_month_completed) / last_month_completed) * 100
    
    # Weekly trends data for chart
    weeks_data = []
    for i in range(4):
        week_start = start_of_month + timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        incoming = ServiceRequest.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        ).count()
        completed = ServiceRequest.objects.filter(
            status=ServiceRequest.Status.COMPLETED,
            preferred_date__gte=week_start,
            preferred_date__lte=week_end
        ).count()
        weeks_data.append({
            'week': f"Week {i+1}",
            'incoming': incoming,
            'completed': completed
        })
    
    # Convert to JSON-safe format for template
    import json
    weeks_data_json = json.dumps(weeks_data)
    
    # Service distribution
    residential = ServiceRequest.objects.filter(
        service_type=ServiceRequest.ServiceType.DECLOGGING
    ).count()
    commercial = ServiceRequest.objects.filter(
        service_type=ServiceRequest.ServiceType.GRASS_CUTTING
    ).count()
    total_services = residential + commercial
    
    residential_pct = (residential / total_services * 100) if total_services > 0 else 0
    commercial_pct = (commercial / total_services * 100) if total_services > 0 else 0
    
    # Barangay ranking
    barangay_stats = (
        ServiceRequest.objects.values('barangay')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    context = {
        'total_requests': total_requests,
        'pending_count': pending_count,
        'completed_this_month': completed_this_month,
        'efficiency_change': efficiency_change,
        'weeks_data': weeks_data_json,
        'residential_pct': round(residential_pct, 1),
        'commercial_pct': round(commercial_pct, 1),
        'barangay_stats': list(barangay_stats),
        'total_services': total_services,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@role_required("ADMIN")
def admin_requests(request):
    """Admin requests view with sub-tabs"""
    tab = request.GET.get('tab', 'pending')
    
    if tab == 'pending':
        requests = ServiceRequest.objects.filter(status=ServiceRequest.Status.PENDING).order_by('-created_at')
    elif tab == 'approved':
        # Show requests that have been approved (have fee computed or payment confirmed)
        requests = ServiceRequest.objects.filter(
            Q(fee_amount__isnull=False) | Q(payment_confirmed_at__isnull=False)
        ).exclude(status=ServiceRequest.Status.PENDING).order_by('-created_at')
    elif tab == 'schedule':
        requests = ServiceRequest.objects.filter(
            schedule__isnull=False
        ).select_related('schedule').order_by('schedule__service_date')
    elif tab == 'completed':
        requests = ServiceRequest.objects.filter(status=ServiceRequest.Status.COMPLETED).order_by('-preferred_date')
    else:
        requests = ServiceRequest.objects.all().order_by('-created_at')
    
    context = {
        'requests': requests,
        'active_tab': tab,
    }
    return render(request, 'dashboard/admin_requests.html', context)


@login_required
@role_required("ADMIN")
def approve_request(request, pk):
    """Approve a pending request"""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        # In a real system, you might change status or create a schedule
        messages.success(request, f'Request {service_request.id} approved successfully.')
        Notification.objects.create(
            user=service_request.consumer,
            message=f'Your service request #{service_request.id} has been approved.'
        )
    return redirect('dashboard:admin_requests')


@login_required
@role_required("ADMIN")
def admin_schedule_by_barangay(request):
    """Schedule view showing customers per barangay with 10-person limit tracking"""
    barangays = (
        Schedule.objects.values('barangay')
        .annotate(count=Count('id'))
        .order_by('barangay')
    )
    
    barangay_details = []
    for barangay in barangays:
        schedules = list(Schedule.objects.filter(barangay=barangay['barangay']).select_related(
            'service_request__consumer', 'assigned_staff'
        )[:10])
        count = len(schedules)
        percentage = (count / 10) * 100 if count > 0 else 0
        
        barangay_details.append({
            'barangay': barangay['barangay'],
            'count': count,
            'percentage': percentage,
            'schedules': schedules,
            'is_full': count >= 10,
        })
    
    context = {
        'barangay_details': barangay_details,
        'active_tab': 'schedule',
    }
    return render(request, 'dashboard/admin_schedule.html', context)


@login_required
@role_required("ADMIN")
def admin_membership(request):
    """Admin membership view with sub-tabs"""
    tab = request.GET.get('tab', 'registration')
    
    if tab == 'registration':
        # Show registration form or pending registrations
        consumers = User.objects.filter(role=User.Role.CONSUMER, is_approved=False)
    elif tab == 'account_management':
        consumers = User.objects.filter(role=User.Role.CONSUMER).select_related('consumer_profile')
    elif tab == 'service_history':
        consumers = User.objects.filter(role=User.Role.CONSUMER).select_related('consumer_profile')
    else:
        consumers = User.objects.filter(role=User.Role.CONSUMER)
    
    context = {
        'consumers': consumers,
        'active_tab': tab,
    }
    return render(request, 'dashboard/admin_membership.html', context)


@login_required
@role_required("ADMIN")
def member_service_history(request, user_id):
    """Service history for a specific member"""
    consumer = get_object_or_404(User, pk=user_id, role=User.Role.CONSUMER)
    service_requests = ServiceRequest.objects.filter(
        consumer=consumer,
        status=ServiceRequest.Status.COMPLETED
    ).order_by('-preferred_date')
    
    # Calculate remaining balance (5 cubic meters per 4 years)
    four_years_ago = date.today() - timedelta(days=4*365)
    recent_services = service_requests.filter(preferred_date__gte=four_years_ago)
    total_cubic_meters = sum(
        getattr(req, 'cubic_meters', 0) for req in recent_services
        if hasattr(req, 'cubic_meters')
    )
    remaining_balance = max(0, 5 - total_cubic_meters)
    
    context = {
        'consumer': consumer,
        'service_requests': service_requests,
        'remaining_balance': remaining_balance,
        'total_used': total_cubic_meters,
    }
    return render(request, 'dashboard/member_service_history.html', context)


@login_required
@role_required("ADMIN")
def admin_computation(request):
    """Cost computation and receipt generation"""
    from dashboard.forms import QuickComputationForm
    
    form = QuickComputationForm()
    computation_result = None
    
    if request.method == 'POST':
        form = QuickComputationForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            location = form.cleaned_data['location']
            cubic_meters = form.cleaned_data['cubic_meters']
            distance = form.cleaned_data.get('distance_km', Decimal('0'))
            meals_transport = form.cleaned_data.get('meals_transport', Decimal('0'))
            
            # Calculate fees
            tipping_fee = cubic_meters * Decimal('500.00')
            inspection_fee = Decimal('150.00')
            
            total = tipping_fee + inspection_fee
            
            # Outside Bayawan calculation
            distance_cost = Decimal('0')
            wear_tear = Decimal('0')
            
            if location == 'outside' and distance:
                round_trip = distance * 2
                distance_cost = round_trip * Decimal('20.00')
                wear_tear = distance_cost * Decimal('0.20')
                total = total + distance_cost + wear_tear + meals_transport
            
            computation_result = {
                'category': category,
                'location': location,
                'cubic_meters': cubic_meters,
                'distance': distance,
                'tipping_fee': tipping_fee,
                'inspection_fee': inspection_fee,
                'distance_cost': distance_cost,
                'wear_tear': wear_tear,
                'meals_transport': meals_transport,
                'total': total,
                'prepared_by': request.user.get_full_name(),
            }
    
    context = {
        'form': form,
        'computation_result': computation_result,
    }
    return render(request, 'dashboard/admin_computation.html', context)


@login_required
@role_required("ADMIN")
def generate_receipt(request):
    """Generate printable receipt"""
    # This would generate a PDF or printable HTML receipt
    # For now, return the computation result as receipt
    return redirect('dashboard:admin_computation')


@login_required
@role_required("ADMIN")
def admin_declogging_app(request):
    """Declogging services application form"""
    if request.method == 'POST':
        # Process form submission
        messages.success(request, 'Application form generated successfully.')
        return redirect('dashboard:admin_declogging_app')
    
    return render(request, 'dashboard/admin_declogging_app.html')
