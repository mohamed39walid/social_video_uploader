from rest_framework import serializers
from .models import VideoPost

class VideoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPost
        fields = [
            "id",
            "title",
            "description",
            "video_file",
            "platforms",
            "youtube_privacy",
            "dailymotion_privacy",
            "vimeo_privacy",
            "youtube_video_id",
            "dailymotion_video_id",
            "vimeo_video_id",
            "upload_status",
            "created_at",
        ]
        read_only_fields = ["youtube_video_id", "dailymotion_video_id", "vimeo_video_id", "upload_status", "created_at"]
