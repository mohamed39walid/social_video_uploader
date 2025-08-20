from django.db import models
from django.utils.html import format_html


class VideoPost(models.Model):

    class Platform(models.TextChoices):
        YOUTUBE = "YT", "YouTube"
        DAILYMOTION = "DM", "Dailymotion"
        VIMEO = "VM", "Vimeo"


    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"


    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to="videos/", blank=True, null=True)
    video_url = models.URLField(blank=True)


    platforms = models.JSONField(default=list, blank=True)


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

    upload_status = models.JSONField(default=dict, blank=True)



    youtube_video_id = models.CharField(max_length=50, blank=True)
    dailymotion_video_id = models.CharField(max_length=50, blank=True)
    vimeo_video_id = models.CharField(max_length=50, blank=True)
    upload_history = models.JSONField(default=list, blank=True)



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
