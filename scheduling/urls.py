from django.urls import path

from . import views

app_name = "scheduling"

urlpatterns = [
    path("", views.schedule_list, name="schedule_list"),
    path("create/<int:request_id>/", views.create_schedule, name="create_schedule"),
    path("<int:pk>/assign/", views.assign_staff, name="assign_staff"),
]
