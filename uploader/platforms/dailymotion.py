
import requests
from urllib.parse import urlencode

CLIENT_ID = "ec1e4db81bc76ba6f7b8"
CLIENT_SECRET = "653187359ab5ce02d7091e86f44710da98b9933e" 
REDIRECT_URI = "http://127.0.0.1:8000/dailymotion/callback/"


AUTH_URL = "https://www.dailymotion.com/oauth/authorize"
TOKEN_URL = "https://api.dailymotion.com/oauth/token"
UPLOAD_URL = "https://api.dailymotion.com/file/upload"
CREATE_VIDEO_URL = "https://api.dailymotion.com/me/videos"


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


import requests


CLIENT_ID = "ec1e4db81bc76ba6f7b8"
CLIENT_SECRET = "653187359ab5ce02d7091e86f44710da98b9933e" 
REDIRECT_URI = "http://127.0.0.1:8000/dailymotion/callback/" 

# API endpoints
AUTH_URL = "https://www.dailymotion.com/oauth/authorize"
TOKEN_URL = "https://api.dailymotion.com/oauth/token"
UPLOAD_URL = "https://api.dailymotion.com/file/upload"
CREATE_VIDEO_URL = "https://api.dailymotion.com/me/videos"



def get_authorization_url(state: str = None):
    url = (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=manage_videos"
    )
    if state:
        url += f"&state={state}"
    return url



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
    return res.json()  


def refresh_access_token(refresh_token: str) -> dict:
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    res = requests.post(TOKEN_URL, data=data)
    res.raise_for_status()
    return res.json()  



def upload_to_dailymotion(file_path: str, title: str, access_token: str, description: str = "",
                          channel: str = "news", published: bool = True, is_for_kids: bool = False) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}


    res = requests.get(UPLOAD_URL, headers=headers)
    try:
        res.raise_for_status()
    except requests.HTTPError:
        raise Exception(f"Upload URL fetch failed. Response: {res.json()}")
    upload_endpoint = res.json()["upload_url"]

    with open(file_path, "rb") as f:
        res = requests.post(upload_endpoint, files={"file": f})
        try:
            res.raise_for_status()
        except requests.HTTPError:
            raise Exception(f"Video upload failed. Response: {res.json()}")
        uploaded_url = res.json()["url"]

    data = {
        "url": uploaded_url,
        "title": title,
        "description": description,
        "channel": channel,
        "published": "true" if published else "false",
        "is_created_for_kids": "true" if is_for_kids else "false",
    }
    res = requests.post(CREATE_VIDEO_URL, headers=headers, data=data)
    try:
        res.raise_for_status()
    except requests.HTTPError:
        raise Exception(f"Video creation failed. Response: {res.json()}")

    return res.json()

def upload_video_flow(request, video):
    access_token = request.session.get("dm_access_token")
    if not access_token:
        return {"redirect": get_authorization_url(state=str(video.id))}
    
    result = upload_to_dailymotion(
        file_path=video.video_file.path,
        title=video.title,
        description=video.description,
        access_token=access_token,
        published=True if video.dailymotion_privacy == "public" else False
    )
    return {"uploaded": True, "video_id": result["id"]}





def check_dailymotion_video_exists(video_id, access_token):
    url = f"https://api.dailymotion.com/video/{video_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        res = requests.get(url, headers=headers)
        return res.status_code == 200
    except Exception:
        return False