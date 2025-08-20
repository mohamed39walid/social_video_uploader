from django.db import models
from django.utils.html import format_html


class VideoPost(models.Model):
    # Supported platforms
    class Platform(models.TextChoices):
        YOUTUBE = "YT", "YouTube"
        DAILYMOTION = "DM", "Dailymotion"
        VIMEO = "VM", "Vimeo"

    # Upload status options
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    # Basic video info
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to="videos/", blank=True, null=True)
    video_url = models.URLField(blank=True)

    # Platforms selected (stored as JSON list)
    platforms = models.JSONField(default=list, blank=True)

    # Privacy settings per platform
    youtube_privacy = models.CharField(
        max_length=10,
        choices=[("public", "Public"), ("private", "Private")],
        default="private"
    )
    dailymotion_privacy = models.CharField(
        max_length=10,
        choices=[("public", "Public"), ("private", "Private")],
        default="private"
    )
    vimeo_privacy = models.CharField(
        max_length=10,
        choices=[("public", "Public"), ("private", "Private")],
        default="private"
    )

    # Upload status per platform (stored as JSON)
    upload_status = models.JSONField(default=dict, blank=True)
    # Example: {"YT": "pending", "DM": "pending", "VM": "pending"}

    # Platform video IDs after upload
    youtube_video_id = models.CharField(max_length=50, blank=True)
    dailymotion_video_id = models.CharField(max_length=50, blank=True)
    vimeo_video_id = models.CharField(max_length=50, blank=True)
    upload_history = models.JSONField(default=list, blank=True)


    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def youtube_link(self, obj):
        if obj.youtube_video_id:
            url = f"https://www.youtube.com/watch?v={obj.youtube_video_id}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, "Watch Video")
        return "-"
    youtube_link.short_description = "YouTube"
    def dailymotion_link(self, obj):
        if obj.dailymotion_video_id:
            url = f"https://www.dailymotion.com/video/{obj.dailymotion_video_id}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, "Watch Video")
        return "-"
    dailymotion_link.short_description = "Dailymotion"


    def __str__(self):
        return self.title
