from django.urls import path
from . import views

urlpatterns = [
    path('send/<str:token>/', views.send_message, name='send_message'),
    path('stream/<str:token>/', views.stream_response, name='stream_response'),
    path('history/<str:token>/', views.get_history, name='get_history'),
]
