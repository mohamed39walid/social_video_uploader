from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import VideoPost
from .utils.youtube_auth import get_youtube_credentials
from .platforms.youtube import upload_to_youtube, check_youtube_video_exists
from .platforms.vimeo_api import upload_to_vimeo, check_vimeo_video_exists
from .platforms.dailymotion import (
    upload_to_dailymotion,
    get_authorization_url,
    check_dailymotion_video_exists,
)
from django.shortcuts import redirect
import requests
import datetime


class VideoPostForm(forms.ModelForm):
    PLATFORM_CHOICES = [
        ("YT", "YouTube"),
        ("DM", "Dailymotion"),
        ("VM", "Vimeo"),
    ]

    platforms = forms.MultipleChoiceField(
        choices=PLATFORM_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Platforms",
    )

    class Meta:
        model = VideoPost
        fields = [
            "title",
            "description",
            "video_file",
            "platforms",
            "youtube_privacy",
            "dailymotion_privacy",
            "vimeo_privacy",
        ]
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Enter video description..."}
            ),
            "youtube_privacy": forms.RadioSelect(
                attrs={"class": "platform-privacy", "data-platform": "YT"}
            ),
            "dailymotion_privacy": forms.RadioSelect(
                attrs={"class": "platform-privacy", "data-platform": "DM"}
            ),
            "vimeo_privacy": forms.RadioSelect(
                attrs={"class": "platform-privacy", "data-platform": "VM"}
            ),
        }


class PlatformFilter(admin.SimpleListFilter):
    title = "Platform"
    parameter_name = "platform"

    def lookups(self, request, model_admin):
        return (
            ("YT", "YouTube"),
            ("DM", "Dailymotion"),
            ("VM", "Vimeo"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(platforms__icontains=self.value())
        return queryset


@admin.register(VideoPost)
class VideoPostAdmin(admin.ModelAdmin):
    form = VideoPostForm
    list_display = (
        "title",
        "platforms_display",
        "youtube_link",
        "vimeo_link",
        "dailymotion_link",
        "show_upload_history",
        "created_at",
    )
    
    def show_upload_history(self, obj):
        if obj.upload_history:
            formatted = ""
            for attempt in obj.upload_history:
                timestamp = attempt.get("timestamp", "")
                platform = attempt.get("platform", "")
                result = attempt.get("result", "")

                formatted += f"{timestamp} - <b>{platform}</b>: {result}<br>"
            return format_html(formatted)
        return "-"

    
    show_upload_history.short_description = "Upload History"
    list_filter = (PlatformFilter, "created_at")
    readonly_fields = ("youtube_link", "vimeo_link", "dailymotion_link")
    actions = ["upload_to_platforms"]

    class Media:
        js = ("admin/js/video_platform_privacy.js",)

    def platforms_display(self, obj):
        return ", ".join(obj.platforms)

    platforms_display.short_description = "Platforms"

    def youtube_link(self, obj):
        if obj.youtube_video_id:
            url = f"https://www.youtube.com/watch?v={obj.youtube_video_id}"
            return format_html('<a href="{}" target="_blank">Watch Video</a>', url)
        return ""

    youtube_link.short_description = "YouTube"

    def vimeo_link(self, obj):
        if obj.vimeo_video_id:
            url = f"https://vimeo.com/{obj.vimeo_video_id}"
            return format_html(
                '<a href="{}" target="_blank">{}</a>', url, obj.vimeo_video_id
            )
        return ""

    vimeo_link.short_description = "Vimeo"

    def dailymotion_link(self, obj):
        """
        Show "Watch Video" link only if dailymotion_video_id exists.
        """
        if obj.dailymotion_video_id:
            url = f"https://www.dailymotion.com/video/{obj.dailymotion_video_id}"
            return format_html(
                '<a href="{}" target="_blank">{}</a>', url, "Watch Video"
            )
        return ""

    dailymotion_link.short_description = "Dailymotion"

    def upload_to_platforms(self, request, queryset):
        for video in queryset:
            upload_status = video.upload_status or {}

            if not video.video_file:
                self.message_user(
                    request, f"No video file for {video.title}", level="error"
                )
                continue


            if "YT" in video.platforms:
                try:
                    creds = ""
                    if video.youtube_video_id:
                        upload_status["YT"] = "exists"
                        result = "exists"
                        self.message_user(
                            request, f"YouTube video already exists for {video.title}"
                        )
                    else:
                        creds = get_youtube_credentials(request)
                        video_id, _ = upload_to_youtube(
                            video_path=video.video_file.path,
                            title=video.title,
                            description=video.description,
                            privacy_status=video.youtube_privacy,
                            credentials=creds,
                        )
                        video.youtube_video_id = video_id
                        upload_status["YT"] = "uploaded"
                        result = "uploaded"
                        self.message_user(request, f"Uploaded {video.title} to YouTube")
                except Exception as e:
                    upload_status["YT"] = "failed"
                    result = "failed"
                    self.message_user(
                        request,
                        f"YouTube upload failed for {video.title}: {e}",
                        level="error",
                    )

                video.upload_history.append({
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "platform": "YT",
                    "result": result
                })
                video.save()

            if "VM" in video.platforms:
                try:
                    if video.vimeo_video_id and check_vimeo_video_exists(
                        video.vimeo_video_id
                    ):
                        upload_status["VM"] = "exists"
                        self.message_user(
                            request, f"Vimeo video already exists for {video.title}"
                        )
                    else:
                        privacy_map = {"public": "anybody", "private": "nobody"}
                        vimeo_id = upload_to_vimeo(
                            video_path=video.video_file.path,
                            title=video.title,
                            description=video.description,
                            privacy=privacy_map.get(video.vimeo_privacy, "nobody"),
                        )
                        video.vimeo_video_id = vimeo_id
                        upload_status["VM"] = "uploaded"
                        self.message_user(request, f"Uploaded {video.title} to Vimeo")
                except Exception as e:
                    upload_status["VM"] = "failed"
                    self.message_user(
                        request,
                        f"Vimeo upload failed for {video.title}: {e}",
                        level="error",
                    )
                video.upload_history.append({
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "platform": "VM",
                "result": result
                })
                video.save()

            if "DM" in video.platforms:
                try:
                    return redirect(f"/dailymotion/login_redirect/{video.id}/")
                    if video.dailymotion_video_id and check_dailymotion_video_exists(
                        video.dailymotion_video_id, access_token
                    ):
                        upload_status["DM"] = "exists"
                        self.message_user(
                            request,
                            f"Dailymotion video already exists for {video.title}",
                        )
                    else:

                        published = video.dailymotion_privacy == "public"
                        res = upload_to_dailymotion(
                            file_path=video.video_file.path,
                            title=video.title,
                            description=video.description,
                            access_token=access_token,
                            published=published,
                            is_for_kids=False,
                        )
                        video.dailymotion_video_id = res["id"]
                        upload_status["DM"] = "uploaded"
                        self.message_user(
                            request, f"Uploaded {video.title} to Dailymotion"
                        )
                except Exception as e:
                    upload_status["DM"] = "failed"
                    self.message_user(
                        request,
                        f"Dailymotion upload failed for {video.title}: {e}",
                        level="error",
                    )
                video.upload_history.append({
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "platform": "DM",
                "result": result
                })
                video.save()
                
                
                
            video.upload_status = upload_status
            video.save()

    upload_to_platforms.short_description = "Upload selected videos to Platforms"
