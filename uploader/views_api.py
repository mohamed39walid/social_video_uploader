from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .platforms.dailymotion import exchange_code_for_token
from .models import VideoPost
from .serializers import VideoPostSerializer
from .utils.youtube_auth import get_youtube_credentials
from .platforms.youtube import upload_to_youtube, check_youtube_video_exists
from .platforms.vimeo_api import upload_to_vimeo, check_vimeo_video_exists
from .platforms.dailymotion import (
    upload_to_dailymotion,
    check_dailymotion_video_exists,
    get_authorization_url,
)



class VideoPostCreateView(APIView):
    def post(self, request):
        serializer = VideoPostSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save()
            return Response(
                {"id": video.id, "message": "VideoPost created"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoPostUploadView(APIView):
    def post(self, request, pk):
        video = get_object_or_404(VideoPost, pk=pk)
        upload_status = video.upload_status or {}

        if not video.video_file:
            return Response({"error": "No video file"}, status=status.HTTP_400_BAD_REQUEST)

        if "YT" in video.platforms:
            try:

                creds = get_youtube_credentials(request)
                if video.youtube_video_id and check_youtube_video_exists(video.youtube_video_id, creds):
                    upload_status["YT"] = "exists"
                else:
                    video_id, _ = upload_to_youtube(
                        video_path=video.video_file.path,
                        title=video.title,
                        description=video.description,
                        privacy_status=video.youtube_privacy,
                        credentials=creds,
                    )
                    video.youtube_video_id = video_id
                    upload_status["YT"] = "uploaded"
            except Exception as e:
                upload_status["YT"] = f"failed: {str(e)}"

        if "VM" in video.platforms:
            try:
                if video.vimeo_video_id and check_vimeo_video_exists(video.vimeo_video_id):
                    upload_status["VM"] = "exists"
                else:
                    privacy_map = {"public": "anybody", "private": "nobody"}
                    vimeo_id = upload_to_vimeo(
                        video_path=video.video_file.path,
                        title=video.title,
                        description=video.description,
                        privacy=privacy_map.get(video.vimeo_privacy, "nobody")
                    )
                    video.vimeo_video_id = vimeo_id
                    upload_status["VM"] = "uploaded"
            except Exception as e:
                upload_status["VM"] = f"failed: {str(e)}"


        if "DM" in video.platforms:
            try:
                access_token = request.session.get("dm_access_token")
                if not access_token:

                    auth_url = get_authorization_url(state=str(video.id))
                    return Response(
                        {"redirect_url": auth_url, "message": "Open this URL in a new tab to login to Dailymotion"},
                        status=status.HTTP_200_OK
                    )

                if video.dailymotion_video_id and check_dailymotion_video_exists(video.dailymotion_video_id, access_token):
                    upload_status["DM"] = "exists"
                else:
                    published = True if video.dailymotion_privacy == "public" else False
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
            except Exception as e:
                upload_status["DM"] = f"failed: {str(e)}"



        video.upload_status = upload_status
        video.save()

        serializer = VideoPostSerializer(video)
        return Response(
            {"upload_status": upload_status, "video": serializer.data},
            status=status.HTTP_200_OK
        )


class VideoPostListView(APIView):

    def get(self, request):
        videos = VideoPost.objects.all()
        serializer = VideoPostSerializer(videos, many=True)
        return Response(serializer.data)



