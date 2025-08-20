import requests
from urllib.parse import urlencode

# ----------------------
# Dailymotion API credentials
# ----------------------
CLIENT_ID = "2d8c6ca17a82d69ac59c"
CLIENT_SECRET = "6b6d4f7b5432e044d7b326d55de18b652f5da292"
REDIRECT_URI = "http://127.0.0.1:8000/dailymotion/callback/"

# ----------------------
# API endpoints
# ----------------------
AUTH_URL = "https://www.dailymotion.com/oauth/authorize"
TOKEN_URL = "https://api.dailymotion.com/oauth/token"
UPLOAD_URL = "https://api.dailymotion.com/file/upload"
CREATE_VIDEO_URL = "https://api.dailymotion.com/me/videos"

# ----------------------
# Step 1: Generate authorization URL
# ----------------------
def get_authorization_url(state: str = None) -> str:
    """
    Generate Dailymotion authorization URL for user login.
    Optional `state` can be used to track which video/admin triggered this.
    """
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "manage_videos",
    }
    if state:
        params["state"] = state
    return f"{AUTH_URL}?{urlencode(params)}"

# ----------------------
# Step 2: Exchange code for access token
# ----------------------
def exchange_code_for_token(code: str) -> dict:
    """
    Exchange authorization code for access token.
    """
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    res = requests.post(TOKEN_URL, data=data)
    res.raise_for_status()
    return res.json()

# ----------------------
# Step 3: Refresh access token
# ----------------------
def refresh_access_token(refresh_token: str) -> dict:
    """
    Refresh an expired access token.
    """
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    res = requests.post(TOKEN_URL, data=data)
    res.raise_for_status()
    return res.json()

# ----------------------
# Step 4: Upload video
# ----------------------
def upload_to_dailymotion(file_path: str, title: str, access_token: str,
                          description: str = "", channel: str = "news",
                          published: bool = True, is_for_kids: bool = False) -> dict:
    """
    Upload a video to Dailymotion using an access token.

    Returns the JSON response from Dailymotion.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Get upload URL
    res = requests.get(UPLOAD_URL, headers=headers)
    res.raise_for_status()
    upload_endpoint = res.json()["upload_url"]

    # 2. Upload the video file
    with open(file_path, "rb") as f:
        res = requests.post(upload_endpoint, files={"file": f})
        res.raise_for_status()
        uploaded_url = res.json()["url"]

    # 3. Create video object
    data = {
        "url": uploaded_url,
        "title": title,
        "description": description,
        "channel": channel,
        "published": "true" if published else "false",
        "is_created_for_kids": "true" if is_for_kids else "false",
    }
    res = requests.post(CREATE_VIDEO_URL, headers=headers, data=data)
    res.raise_for_status()
    return res.json()

# ----------------------
# Step 5: Full flow helper (user-friendly)
# ----------------------
def upload_video_flow(request, video, is_for_kids: bool = False):
    """
    Handles user-friendly upload flow:
    1. Checks if access token exists in session.
    2. If not, returns a redirect URL for user login.
    3. If token exists, uploads the video immediately.
    """
    access_token = request.session.get("dm_access_token")
    
    if not access_token:
        # Return redirect URL to Dailymotion login
        return {"redirect": get_authorization_url(state=str(video.id))}
    
    # Upload directly
    result = upload_to_dailymotion(
        file_path=video.video_file.path,
        title=video.title,
        description=video.description,
        access_token=access_token,
        published=True if video.dailymotion_privacy == "public" else False,
        is_for_kids=is_for_kids
    )
    return {"uploaded": True, "video_id": result["id"]}
