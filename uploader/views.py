from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from .platforms import dailymotion
from .models import VideoPost

def dailymotion_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state") 
    if not code:
        return HttpResponse("No code parameter received.")

    try:
        tokens = dailymotion.exchange_code_for_token(code)
        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")

        request.session["dm_access_token"] = access_token
        request.session["dm_refresh_token"] = refresh_token

        if state:
            try:
                video = VideoPost.objects.get(id=state)
                result = dailymotion.upload_to_dailymotion(
                    file_path=video.video_file.path,
                    title=video.title,
                    description=video.description,
                    access_token=access_token,
                    published=True if video.dailymotion_privacy == "public" else False
                )
                video.dailymotion_video_id = result["id"]
                upload_status = video.upload_status or {}
                upload_status["DM"] = "uploaded"
                video.upload_status = upload_status
                video.save()
                return redirect("/admin/uploader/videopost/")
            except VideoPost.DoesNotExist:
                return HttpResponse("Video not found for automatic upload.")
            except Exception as e:
                return HttpResponse(f"Video upload failed: {e}")

        return JsonResponse({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": tokens.get("expires_in"),
        })

    except Exception as e:
        return HttpResponse(f"Error exchanging code for token: {e}")


def dailymotion_login_redirect(request, video_id):
    url = dailymotion.get_authorization_url(state=str(video_id))
    return redirect(url)
