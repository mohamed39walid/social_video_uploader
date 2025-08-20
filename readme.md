# Social Video Uploader

A Django-based video uploader that allows administrators to upload videos to **YouTube**, **Vimeo**, and **Dailymotion** directly from the Django admin panel. Supports OAuth authentication, automatic uploads, privacy settings, and upload history tracking.

---

## Features

* Upload videos to multiple platforms from Django admin
* Supports **YouTube**, **Vimeo**, and **Dailymotion**
* OAuth 2.0 authentication for secure platform access
* Privacy settings: `public` / `private`
* Automatic upload upon authorization
* Upload history tracking with timestamp and platform result
* Check if video already exists on the platform before uploading
* Friendly error handling and notifications in admin panel

---

## Technologies Used

* Python 3.11+
* Django 5.x+
* YouTube Data API v3
* Vimeo API
* Dailymotion API
* SQLite / PostgreSQL (or any Django-supported DB)
* Requests library for API calls

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/video-uploader.git
cd video-uploader
```

2. **Create a virtual environment and activate**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Apply migrations**

```bash
python manage.py migrate
```

5. **Create superuser**

```bash
python manage.py createsuperuser
```

6. **Run the server**

```bash
python manage.py runserver
```

---

## Configuration

### YouTube

1. Enable **YouTube Data API v3** in Google Cloud Console.
2. Create OAuth credentials and download `client_secret.json`.
3. Configure your `settings.py` or use your Django admin to store credentials.
4. Ensure the account is verified to avoid upload limits.

### Vimeo

1. Create a Vimeo developer app: [https://developer.vimeo.com/apps](https://developer.vimeo.com/apps)
2. Obtain your **Access Token** and configure it in `vimeo_api.py`.
3. Set desired privacy level: `anybody` (public) or `nobody` (private).

### Dailymotion

1. Create a Dailymotion app: [https://developer.dailymotion.com/](https://developer.dailymotion.com/)
2. Get `CLIENT_ID`, `CLIENT_SECRET` and set `REDIRECT_URI` in `dailymotion.py`.
3. OAuth flow will handle authorization and video upload automatically.

---

## Usage

1. Go to Django Admin panel: `http://127.0.0.1:8000/admin/`
2. Navigate to **Video Posts** and add a new video with:

   * Title
   * Description
   * Video file
   * Selected platforms (YT, DM, VM)
   * Privacy settings per platform
3. Use **Upload to Platforms** action to upload videos.
4. Upload history will be displayed for each video post.

---

## Error Handling

* **YouTube uploadLimitExceeded** → Occurs if the account exceeded daily upload limit. Verify account or switch to another account.
* **Dailymotion upload\_limit\_exceeded** → New accounts may hit daily upload limits. Wait or create another account.
* **Vimeo errors** → Ensure proper access token and privacy settings.

---

## Project Structure

```
video-uploader/
├── uploader/
│   ├── platforms/
│   │   ├── youtube.py
│   │   ├── vimeo_api.py
│   │   └── dailymotion.py
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   └── urls.py
├── media/
├── static/
├── templates/
├── manage.py
└── README.md
```

