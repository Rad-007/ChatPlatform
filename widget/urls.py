from django.urls import path
from . import views

urlpatterns = [
    path('embed/<str:token>.js', views.embed_js, name='embed_js'),
    path('b/<str:token>/', views.widget_page, name='widget_page'),
]
