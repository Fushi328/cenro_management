"""
Authentication middleware to enforce login requirement
"""
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Middleware that requires users to be logged in.
    Allows access to:
    - /accounts/login/ (login page)
    - /accounts/logout/ (logout)
    - /accounts/register/ (registration pages)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Pages that don't require login
        self.public_paths = [
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/register/consumer/',
            '/accounts/register/staff/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Check if path is public
        is_public = any(request.path.startswith(path) for path in self.public_paths)
        
        # If not public and not authenticated, redirect to login
        if not is_public and not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        
        response = self.get_response(request)
        return response
