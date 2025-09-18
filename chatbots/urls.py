from django.urls import path
from . import views

app_name = "chatbots"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.bot_create, name="bot_create"),
    path("<int:pk>/edit/", views.bot_edit, name="bot_edit"),
    path("<int:pk>/delete/", views.bot_delete, name="bot_delete"),
    path("<int:pk>/embed/", views.bot_embed, name="bot_embed"),
]
