from functools import wraps
from typing import Callable

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .models import User


def role_required(*roles: str) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @login_required
        @wraps(view_func)
        def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user: User = request.user  # type: ignore[assignment]
            if not user.is_authenticated:
                return redirect("accounts:login")
            # Superuser (super admin) can access any role-protected page
            if not user.is_superuser and user.role not in roles:
                messages.error(request, "You do not have permission to access this page.")
                return redirect("dashboard:home")
            if not user.is_approved and user.role != User.Role.ADMIN and not user.is_superuser:
                messages.warning(request, "Your account is pending approval from an administrator.")
                return redirect("dashboard:home")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

