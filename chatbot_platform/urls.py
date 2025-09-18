"""Project URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("dashboard/", include("chatbots.urls")),
    path("accounts/", include("accounts.urls")),
    path("widget/", include("widget.urls")),
    path("api/", include("conversations.urls")),
    path("payments/", include("payments.urls")),
]
