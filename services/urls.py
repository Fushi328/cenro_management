from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("request/create/", views.create_request, name="create_request"),
    path("api/reverse-geocode/", views.reverse_geocode, name="reverse_geocode"),
    path("request/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/", views.request_list, name="request_list"),
    path("history/", views.history, name="history"),
    path("clients/", views.client_records, name="client_records"),
    path("request/<int:pk>/compute-fee/", views.compute_fee, name="compute_fee"),
    path("request/<int:pk>/confirm-payment/", views.confirm_payment, name="confirm_payment"),
    path("request/<int:pk>/complete/", views.complete_request, name="complete_request"),
]
