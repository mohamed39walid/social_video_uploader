from django.urls import path
from . import views

urlpatterns = [
    path(
        "dailymotion/login_redirect/<int:video_id>/",
        views.dailymotion_login_redirect,
        name="dailymotion_login_redirect",
    ),  
    path(
        "dailymotion/callback/", views.dailymotion_callback, name="dailymotion_callback"
    ),
]
