from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

def upload_to_youtube(video_path, title, description, privacy_status, credentials):
    youtube = build('youtube', 'v3', credentials=credentials)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(video_path)
    )
    response = request.execute()

    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    return video_id, video_url



def check_youtube_video_exists(video_id: str, credentials) -> bool:
    """
    Check if a YouTube video exists.

    Args:
        video_id: YouTube video ID
        credentials: Google OAuth2 credentials object

    Returns:
        True if video exists, False otherwise
    """
    if not video_id:
        return False  # No ID, video does not exist

    try:
        youtube = build('youtube', 'v3', credentials=credentials)
        response = youtube.videos().list(part="id", id=video_id).execute()
        return len(response.get("items", [])) > 0
    except HttpError:
        return False
    except Exception:
        return False
