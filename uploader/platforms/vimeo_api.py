# platforms/vimeo_api.py

import random

def upload_to_vimeo(video_path, title, description, privacy="nobody"):
    """
    Simulate Vimeo upload.
    Returns a fake Vimeo video ID.
    """
    # Normally here you'd call the real Vimeo API
    print(f"Simulating Vimeo upload for: {title}")
    fake_video_id = f"SIM_VIMEO_{random.randint(1000, 9999)}"
    return fake_video_id
