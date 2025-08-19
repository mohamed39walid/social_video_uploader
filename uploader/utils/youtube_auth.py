# uploader/utils/youtube_auth.py
from django.core.cache import cache
from google_auth_oauthlib.flow import InstalledAppFlow
import os

def get_youtube_credentials(request):
    # Update this to your new credentials file
    client_secret_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # uploader/utils
        "credentials",
        "client_secret_39292969067-t4m5gpqpraq65svmqjn3gtbjhra9ie25.apps.googleusercontent.com.json"
    )

    # Make sure the file exists
    if not os.path.exists(client_secret_path):
        raise FileNotFoundError(f"Client secret file not found at {client_secret_path}")

    flow = InstalledAppFlow.from_client_secrets_file(
        client_secret_path,
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    
    credentials = flow.run_local_server(port=0)
    cache.set(f'youtube_creds_{request.user.id}', credentials.to_json())
    
    return credentials
