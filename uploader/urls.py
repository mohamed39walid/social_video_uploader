from django.urls import path
from . import views

urlpatterns = [
    path('dailymotion/callback/', views.dailymotion_callback, name='dailymotion_callback'),
]
