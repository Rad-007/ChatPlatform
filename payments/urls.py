from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("upgrade/", views.upgrade, name="upgrade"),
    path("verify/", views.verify, name="verify"),
]
