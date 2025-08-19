# platforms/dailymotion.py
import requests

# Hardcoded credentials
CLIENT_ID = "2d89f24e2205b60ce04b"
CLIENT_SECRET = "a150c7599a5cddfe66d395d624ff49f863d5a9a2"
REDIRECT_URI = "http://127.0.0.1:8000/dailymotion/callback"

# API endpoints
AUTH_URL = "https://www.dailymotion.com/oauth/authorize"
TOKEN_URL = "https://api.dailymotion.com/oauth/token"
UPLOAD_URL = "https://api.dailymotion.com/file/upload"
CREATE_VIDEO_URL = "https://api.dailymotion.com/me/videos"


def get_authorization_url():
    """
    Step 1: Redirect user to Dailymotion login to get authorization code
    """
    return (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=manage_videos"
    )


def exchange_code_for_token(code: str) -> dict:
    """
    Step 2: Exchange authorization code for access/refresh token
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
    return res.json()  # { "access_token": "...", "refresh_token": "...", "expires_in": ... }


def refresh_access_token(refresh_token: str) -> dict:
    """
    Step 3: Refresh an expired access token
    """
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    res = requests.post(TOKEN_URL, data=data)
    res.raise_for_status()
    return res.json()  # { "access_token": "...", "expires_in": ... }


def upload_to_dailymotion(file_path: str, title: str, access_token: str, description: str = "", 
                 channel: str = "news", published: bool = True) -> dict:
    """
    Step 4: Upload a video to Dailymotion
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Get upload URL
    res = requests.get(UPLOAD_URL, headers=headers)
    res.raise_for_status()
    upload_endpoint = res.json()["upload_url"]

    # 2. Upload file
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
    }
    res = requests.post(CREATE_VIDEO_URL, headers=headers, data=data)
    res.raise_for_status()
    return res.json()  # { "id": "x123abc", "title": "...", ... }
