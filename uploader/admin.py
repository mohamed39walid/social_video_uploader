from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import VideoPost
from .utils.youtube_auth import get_youtube_credentials
from .platforms.youtube import upload_to_youtube
from .platforms.vimeo_api import upload_to_vimeo 
from .platforms.dailymotion import upload_to_dailymotion  # fixed import
from django.shortcuts import redirect


# ----------------------
# VideoPost Form
# ----------------------
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
        label="Platforms"
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
            "description": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Enter video description..."
            }),
            "youtube_privacy": forms.RadioSelect(attrs={
                "class": "platform-privacy",
                "data-platform": "YT"
            }),
            "dailymotion_privacy": forms.RadioSelect(attrs={
                "class": "platform-privacy",
                "data-platform": "DM"
            }),
            "vimeo_privacy": forms.RadioSelect(attrs={
                "class": "platform-privacy",
                "data-platform": "VM"
            }),
        }


# ----------------------
# Platform Filter
# ----------------------
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


# ----------------------
# Admin
# ----------------------
@admin.register(VideoPost)
class VideoPostAdmin(admin.ModelAdmin):
    form = VideoPostForm
    list_display = (
        "title",
        "platforms_display",
        "youtube_link",
        "vimeo_link",
        "dailymotion_link",
        "created_at",
    )
    list_filter = (PlatformFilter, "created_at")
    readonly_fields = (
        "youtube_link",
        "vimeo_link",
        "dailymotion_link",
    )
    actions = ["upload_to_platforms"]

    class Media:
        js = ("admin/js/video_platform_privacy.js",)

    # ----------------------
    # Display Helpers
    # ----------------------
    def platforms_display(self, obj):
        return ", ".join(obj.platforms)
    platforms_display.short_description = "Platforms"

    def youtube_link(self, obj):
        if obj.youtube_video_id:
            url = f"https://www.youtube.com/watch?v={obj.youtube_video_id}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, "Watch Video")
        return "-"
    youtube_link.short_description = "YouTube"

    def vimeo_link(self, obj):
        if obj.vimeo_video_id:
            url = f"https://vimeo.com/{obj.vimeo_video_id}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.vimeo_video_id)
        return "-"
    vimeo_link.short_description = "Vimeo"

    def dailymotion_link(self, obj):
        if obj.dailymotion_video_id:
            url = f"https://www.dailymotion.com/video/{obj.dailymotion_video_id}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, "Watch Video")
        return "-"
    dailymotion_link.short_description = "Dailymotion"

    # ----------------------
    # Upload Action
    # ----------------------
    def upload_to_platforms(self, request, queryset):
        for video in queryset:
            upload_status = video.upload_status or {}

            if not video.video_file:
                self.message_user(request, f"No video file for {video.title}", level="error")
                continue

            # ----------------------
            # YouTube
            # ----------------------
            if "YT" in video.platforms:
                try:
                    creds = get_youtube_credentials(request)
                    video_id = upload_to_youtube(
                        video_path=video.video_file.path,
                        title=video.title,
                        description=video.description,
                        privacy_status=video.youtube_privacy,
                        credentials=creds,
                    )
                    if isinstance(video_id, tuple):
                        video_id = video_id[0]
                    video.youtube_video_id = video_id
                    upload_status["YT"] = "uploaded"
                    self.message_user(request, f"Uploaded {video.title} to YouTube")
                except Exception as e:
                    upload_status["YT"] = "failed"
                    self.message_user(request, f"YouTube upload failed for {video.title}: {e}", level="error")

            # ----------------------
            # Vimeo
            # ----------------------
            if "VM" in video.platforms:
                try:
                    privacy_map = {"public": "anybody", "private": "nobody"}
                    vimeo_id = upload_to_vimeo(
                        video_path=video.video_file.path,
                        title=video.title,
                        description=video.description,
                        privacy=privacy_map.get(video.vimeo_privacy, "nobody")
                    )
                    video.vimeo_video_id = vimeo_id
                    upload_status["VM"] = "uploaded"
                    self.message_user(request, f"Uploaded {video.title} to Vimeo")
                except Exception as e:
                    upload_status["VM"] = "failed"
                    self.message_user(request, f"Vimeo upload failed for {video.title}: {e}", level="error")

            # ----------------------
            # Dailymotion
            # ----------------------
            if "DM" in video.platforms:
                return redirect(f"/dailymotion/login_redirect/{video.id}/")

                try:
                    # Get access token from session
                    access_token = request.session.get("dm_access_token")

                    if not access_token:
                        # Redirect to Dailymotion login with state = VideoPost ID
                        return redirect(f"/dailymotion/login_redirect/{video.id}/")

                    # Upload video if access token exists
                    published = True if video.dailymotion_privacy == "public" else False
                    res = upload_to_dailymotion(
                        file_path=video.video_file.path,
                        title=video.title,
                        description=video.description,
                        published=published,
                        access_token=access_token,
                        is_for_kids=False  # Required to fix 400 error
                    )

                    # Save video ID and status
                    video.dailymotion_video_id = res["id"]
                    upload_status["DM"] = "uploaded"
                    self.message_user(request, f"Uploaded {video.title} to Dailymotion")

                except Exception as e:
                    upload_status["DM"] = "failed"
                    self.message_user(
                        request,
                        f"Dailymotion upload failed for {video.title}: {e}",
                        level="error"
                    )

            # ----------------------
            # Save updated status
            # ----------------------
            video.upload_status = upload_status
            video.save()

    upload_to_platforms.short_description = "Upload selected videos to Platforms"
