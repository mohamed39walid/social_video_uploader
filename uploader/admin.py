from django.contrib import admin
from django import forms
from .models import VideoPost
# Register your models here.


class VideoPostForm(forms.ModelForm):
    class Meta:
        model = VideoPost
        fields = "__all__"
        widgets = {
            'platforms': forms.RadioSelect,
            'description': forms.Textarea(attrs={'rows': 4})
        }
@admin.register(VideoPost)
class VideoPostAdmin(admin.ModelAdmin):
    form = VideoPostForm
    list_display = (
        'title',
        'get_platforms_display',
        'get_upload_status_display',
        'created_at',
        'updated_at')
    
    list_filter = (
        'platforms',
        'upload_status',
        'created_at'
    )
    search_fields = (
        'title',
        'description'
    )
    list_display_links = ('title',) 