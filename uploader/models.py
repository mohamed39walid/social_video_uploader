from django.db import models

# Create your models here.


class VideoPost(models.Model):
    class Platform(models.TextChoices):
        YOUTUBE = 'YT', 'Youtube'
        VIMEO = 'VM', 'Vimeo',
        Dailymotion = 'DM', 'Dailymotion'
        
    class Status(models.TextChoices):
        PENDING = 'P', "Pending"
        SUCCESS = 'S', "Success"
        FAILED = 'F', 'Failed'
        
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    platforms = models.CharField(
        max_length=2,
        choices = Platform.choices,
        default=Platform.YOUTUBE
    )
    upload_status = models.CharField(
        max_length=2,
        choices= Status.choices,
        default= Status.PENDING
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.title} ({self.get_platforms_display()})"