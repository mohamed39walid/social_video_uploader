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


# ----------------------
# Check if Vimeo video exists (simulated)
# ----------------------
def check_vimeo_video_exists(video_id: str) -> bool:
    """
    Simulate checking if a Vimeo video exists.

    Args:
        video_id: Vimeo video ID

    Returns:
        True if video exists, False otherwise (simulated)
    """
    # Normally, you'd call the real Vimeo API:
    # GET https://api.vimeo.com/videos/{video_id} with OAuth token
    print(f"Checking if Vimeo video exists: {video_id}")

    if video_id:
        import random

        return random.random() < 0.8
    return False
