import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file if running locally
load_dotenv(".env")

PAGE_ID = os.getenv("PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
output_dir = "output"
VIDEO_NAME = environ.get("VIDEO_NAME", "video.mp4")
def initialize_upload_session(page_id, page_access_token):
    url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "upload_phase": "start",
        "access_token": page_access_token
    }
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    return response_data

def upload_video(video_file_path, upload_url, page_access_token):
    file_size = os.path.getsize(video_file_path)
    headers = {
        "Authorization": f"OAuth {page_access_token}",
        "offset": "0",
        "file_size": str(file_size)
    }
    with open(video_file_path, 'rb') as video_file:
        response = requests.post(upload_url, headers=headers, data=video_file)
    response_data = response.json()
    return response_data

def publish_reel(page_id, page_access_token, video_id, description):
    url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    payload = {
        "access_token": page_access_token,
        "video_id": video_id,
        "upload_phase": "finish",
        "video_state": "PUBLISHED",
        "description": description
    }
    response = requests.post(url, data=payload)
    response_data = response.json()
    return response_data

# Main workflow
session_data = initialize_upload_session(PAGE_ID, PAGE_ACCESS_TOKEN)
print("Session Data:", session_data)

video_file_path = f"{output_dir}/{VIDEO_NAME}"
upload_url = session_data["upload_url"]
upload_response = upload_video(video_file_path, upload_url, PAGE_ACCESS_TOKEN)
print("Upload Response:", upload_response)

description = "What a beautiful day! #sunnyand72"
video_id = session_data["video_id"]
publish_response = publish_reel(PAGE_ID, PAGE_ACCESS_TOKEN, video_id, description)
print("Publish Response:", publish_response)
