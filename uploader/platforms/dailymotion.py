# platforms/dailymotion.py
import requests
from urllib.parse import urlencode

# ----------------------
# Hardcoded credentials
# ----------------------
CLIENT_ID = "2d8c6ca17a82d69ac59c"        # Replace with your Client ID
CLIENT_SECRET = "6b6d4f7b5432e044d7b326d55de18b652f5da292"  # Replace with your Client Secret
REDIRECT_URI = "http://127.0.0.1:8000/dailymotion/callback/"  # Must match app

# API endpoints
AUTH_URL = "https://www.dailymotion.com/oauth/authorize"
TOKEN_URL = "https://api.dailymotion.com/oauth/token"
UPLOAD_URL = "https://api.dailymotion.com/file/upload"
CREATE_VIDEO_URL = "https://api.dailymotion.com/me/videos"

# ----------------------
# Step 1: Generate authorization URL
# ----------------------
def get_authorization_url(state=None):
    """
    Generate Dailymotion authorization URL for user login.
    `state` can be used to remember which video/admin triggered this.
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
    try:
        res.raise_for_status()
    except requests.HTTPError:
        raise Exception(f"Token exchange failed. Response: {res.json()}")
    return res.json()  # {"access_token": "...", "refresh_token": "...", "expires_in": ...}

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
    return res.json()  # {"access_token": "...", "expires_in": ...}

# ----------------------
# Step 4: Upload video
# ----------------------
# platforms/dailymotion.py
import requests

# ----------------------
# Hardcoded credentials
# ----------------------
CLIENT_ID = "2d8c6ca17a82d69ac59c"        # Replace with your Client ID
CLIENT_SECRET = "6b6d4f7b5432e044d7b326d55de18b652f5da292"  # Replace with your Client Secret
REDIRECT_URI = "http://127.0.0.1:8000/dailymotion/callback/"  # Must match app

# API endpoints
AUTH_URL = "https://www.dailymotion.com/oauth/authorize"
TOKEN_URL = "https://api.dailymotion.com/oauth/token"
UPLOAD_URL = "https://api.dailymotion.com/file/upload"
CREATE_VIDEO_URL = "https://api.dailymotion.com/me/videos"


# ----------------------
# Step 1: Generate authorization URL
# ----------------------
def get_authorization_url(state: str = None):
    """
    Step 1: Redirect user to Dailymotion login to get authorization code
    Optional `state` can be passed to identify the video or user.
    """
    url = (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=manage_videos"
    )
    if state:
        url += f"&state={state}"
    return url


# ----------------------
# Step 2: Exchange code for access token
# ----------------------
def exchange_code_for_token(code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    res = requests.post(TOKEN_URL, data=data)
    try:
        res.raise_for_status()
    except requests.HTTPError:
        raise Exception(f"Token exchange failed. Response: {res.json()}")
    return res.json()  # {"access_token": "...", "refresh_token": "...", "expires_in": ...}


# ----------------------
# Step 3: Refresh access token
# ----------------------
def refresh_access_token(refresh_token: str) -> dict:
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    res = requests.post(TOKEN_URL, data=data)
    res.raise_for_status()
    return res.json()  # {"access_token": "...", "expires_in": ...}


# ----------------------
# Step 4: Upload video
# ----------------------
def upload_to_dailymotion(file_path: str, title: str, access_token: str, description: str = "",
                          channel: str = "news", published: bool = True, is_for_kids: bool = False) -> dict:
    """
    Upload a video to Dailymotion using an access token.

    Args:
        file_path: Local path to video file
        title: Video title
        access_token: OAuth2 access token
        description: Video description
        channel: Video channel (default "news")
        published: Whether video should be public
        is_for_kids: Required by Dailymotion when publishing
    Returns:
        JSON response from Dailymotion API
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Get upload URL
    res = requests.get(UPLOAD_URL, headers=headers)
    try:
        res.raise_for_status()
    except requests.HTTPError:
        raise Exception(f"Upload URL fetch failed. Response: {res.json()}")
    upload_endpoint = res.json()["upload_url"]

    # 2. Upload file
    with open(file_path, "rb") as f:
        res = requests.post(upload_endpoint, files={"file": f})
        try:
            res.raise_for_status()
        except requests.HTTPError:
            raise Exception(f"Video upload failed. Response: {res.json()}")
        uploaded_url = res.json()["url"]

    # 3. Create video object
    data = {
        "url": uploaded_url,
        "title": title,
        "description": description,
        "channel": channel,
        "published": "true" if published else "false",
        "is_created_for_kids": "true" if is_for_kids else "false",  # Required by Dailymotion
    }
    res = requests.post(CREATE_VIDEO_URL, headers=headers, data=data)
    try:
        res.raise_for_status()
    except requests.HTTPError:
        raise Exception(f"Video creation failed. Response: {res.json()}")

    return res.json()  # {"id": "x123abc", "title": "...", ...}
# ----------------------
# Step 5: Full flow helper
# ----------------------
def upload_video_flow(request, video):
    """
    Handles user-friendly flow:
    1. Check for stored access token.
    2. If missing, redirect user to login.
    3. If token exists, upload video immediately.
    """
    # Example: access token stored in session per user
    access_token = request.session.get("dm_access_token")
    if not access_token:
        # Redirect user to Dailymotion login
        return {"redirect": get_authorization_url(state=str(video.id))}
    
    # Otherwise, upload directly
    result = upload_to_dailymotion(
        file_path=video.video_file.path,
        title=video.title,
        description=video.description,
        access_token=access_token,
        published=True if video.dailymotion_privacy == "public" else False
    )
    return {"uploaded": True, "video_id": result["id"]}





# ----------------------
# Step 6: Check if Dailymotion video exists
# ----------------------
def check_dailymotion_video_exists(video_id, access_token):
    url = f"https://api.dailymotion.com/video/{video_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        res = requests.get(url, headers=headers)
        return res.status_code == 200
    except Exception:
        return False