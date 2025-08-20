from django.urls import path
from .views_api import VideoPostCreateView, VideoPostUploadView, VideoPostListView

urlpatterns = [
    path("videos/", VideoPostListView.as_view(), name="video-list"),
    path("videos/create/", VideoPostCreateView.as_view(), name="video-create"),
    path("videos/<int:pk>/upload/", VideoPostUploadView.as_view(), name="video-upload"),
]
