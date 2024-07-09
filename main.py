import os
import base64
import requests
import smtplib
from os import environ
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from textwrap import fill, shorten
from pyfiglet import Figlet
from videoProcess.Quote import get_quote
from videoProcess.SoundCreate import make_audio
from videoProcess.VideoDownload import download_video
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# Load environment variables from .env file if running locally
load_dotenv(".env")

# Constants and configuration
CLIENT_ID = environ.get("CLIENT_ID")
CLIENT_SECRET = environ.get("CLIENT_SECRET")
REFRESH_TOKEN = environ.get("REFRESH_TOKEN")
AUDIO_NAME = environ.get("AUDIO_NAME", "audio.mp3")
VIDEO_NAME = environ.get("VIDEO_NAME", "video.mp4")
FINAL_VIDEO = environ.get("FINAL_VIDEO", "final_video.mp4")
EMAIL_USER = environ.get("EMAIL_USER")
EMAIL_PASS = environ.get("EMAIL_PASS")
EMAIL_TO = environ.get("EMAIL_TO")
PAGE_ID = environ.get("PAGE_ID")
PAGE_ACCESS_TOKEN = environ.get("PAGE_ACCESS_TOKEN")
IG_USER_ID = environ.get("IG_USER_ID")
IG_ACCESS_TOKEN = environ.get("IG_ACCESS_TOKEN")

# Ensure output directory exists
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Display a title using Figlet
fig_font = Figlet(font="slant", justify="left")
print(fig_font.renderText("Auto Video Short!!!"))

# Get a quote and save it to a variable
text_quote = get_quote()
make_audio(text_quote)

# Save the quote to a text file
quote_file_path = os.path.join(output_dir, "quote.txt")
with open(quote_file_path, "w") as file:
    file.write(shorten(text_quote, width=90, placeholder="..."))
print(f"Quote saved to {quote_file_path}")

# Download the video clip from an API
download_video()

# Verify that the necessary files exist
audio_path = f"{output_dir}/{AUDIO_NAME}"
video_path = f"{output_dir}/{VIDEO_NAME}"

if not os.path.exists(audio_path):
    print(f"Error: Audio file {audio_path} does not exist.")
    exit(1)

if not os.path.exists(video_path):
    print(f"Error: Video file {video_path} does not exist.")
    exit(1)

# Prepare the quote text for the video
text_quote = fill(text_quote, width=30, fix_sentence_endings=True)

# Set the resolution for the final video
resolution = (1080, 1920)

# Load the audio clip
audio_clip = AudioFileClip(audio_path)

try:
    # Load the video clip, set the audio, loop the video, and resize
    video_clip = VideoFileClip(video_path, audio=False).set_audio(audio_clip).loop(duration=audio_clip.duration).resize(resolution)

    # Create a text clip with the quote
    fact_text = TextClip(text_quote, color='white', fontsize=50).set_position(('center', 'center'))

    # Get the size of the text clip
    fact_text_width, fact_text_height = fact_text.size

    # Create a semi-transparent black background clip with the same size as the text clip
    semi_transparent_bg = ColorClip(size=(fact_text_width, fact_text_height), color=(0, 0, 0)).set_opacity(0.5).set_position(('center', 'center'))
    final = CompositeVideoClip([video_clip, semi_transparent_bg.set_duration(video_clip.duration),
                                fact_text.set_duration(video_clip.duration)])
    # Export the final video
    final_video_path = f"{output_dir}/{FINAL_VIDEO}"
    final.subclip(0, video_clip.duration).write_videofile(final_video_path, fps=30, codec='libx264')
    print(f"Final video successfully created at {final_video_path}")
except Exception as e:
    print(f"Error processing video: {e}")

# Convert video to base64
def video_to_base64(video_path):
    with open(video_path, "rb") as video_file:
        base64_encoded_video = base64.b64encode(video_file.read()).decode('utf-8')
    return base64_encoded_video

base64_video = video_to_base64(final_video_path)

def send_email(subject, body, to, base64_video):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to
    msg['Subject'] = subject

    html = f"""
    <div class="video-container">
            <video controls>
                <source src="data:video/mp4;base64,{base64_video}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <p>Quote: {text_quote}</p>
    """

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    text = msg.as_string()
    server.sendmail(EMAIL_USER, to, text)
    server.quit()
    print(f"Email sent to {to} with embedded video")

send_email(
    subject=text_quote,
    body="Please find the embedded video below.",
    to=EMAIL_TO,
    base64_video=base64_video
)

def upload_video_to_facebook(video_file_path, page_id, page_access_token, video_title, video_description):
    try:
        # Initiate the upload
        init_url = f"https://graph-video.facebook.com/v12.0/{page_id}/videos"
        init_params = {
            "upload_phase": "start",
            "access_token": page_access_token,
            "file_size": os.path.getsize(video_file_path)
        }
        init_response = requests.post(init_url, data=init_params).json()
        print("Init response:", init_response)

        if 'upload_session_id' not in init_response:
            raise ValueError(f"Failed to initiate upload: {init_response}")

        upload_session_id = init_response['upload_session_id']
        video_id = init_response['video_id']

        # Upload the video file
        with open(video_file_path, 'rb') as video_file:
            video_data = video_file.read()
        upload_url = f"https://graph-video.facebook.com/v12.0/{page_id}/videos"
        upload_params = {
            "upload_phase": "transfer",
            "access_token": page_access_token,
            "upload_session_id": upload_session_id,
            "start_offset": 0,
            "video_file_chunk": video_data
        }
        upload_response = requests.post(upload_url, files={"video_file_chunk": video_data}, data=upload_params).json()
        print("Upload response:", upload_response)

        if 'start_offset' not in upload_response or upload_response['start_offset'] != '0':
            raise ValueError(f"Failed to upload video: {upload_response}")

        # Finish the upload
        finish_url = f"https://graph-video.facebook.com/v12.0/{page_id}/videos"
        finish_params = {
            "upload_phase": "finish",
            "access_token": page_access_token,
            "upload_session_id": upload_session_id,
            "title": video_title,
            "description": video_description
        }
        finish_response = requests.post(finish_url, data=finish_params).json()
        print("Finish response:", finish_response)

        return finish_response
    except Exception as e:
        print(f"Error uploading video: {e}")
        return {"error": str(e)}

# Example usage
video_title = text_quote
video_description = text_quote
video_file_path = f"{output_dir}/{FINAL_VIDEO}"

response = upload_video_to_facebook(video_file_path, PAGE_ID, PAGE_ACCESS_TOKEN, video_title, video_description)

if 'success' in response:
    print('Video uploaded successfully!')
    print('Response:', response)
else:
    print('Failed to upload video.')
    print('Response:', response)

def upload_video_to_instagram(video_file_path, caption, access_token, ig_user_id):
    try:
        # Step 1: Upload the video
        upload_url = f"https://graph.facebook.com/v15.0/{ig_user_id}/media"
        video_params = {
            'access_token': access_token,
            'media_type': 'VIDEO',
            'video_url': video_file_path,
            'caption': caption
        }

        upload_response = requests.post(upload_url, data=video_params).json()
        if 'id' not in upload_response:
            raise ValueError(f"Error uploading video: {upload_response}")

        creation_id = upload_response['id']

        # Step 2: Publish the video
        publish_url = f"https://graph.facebook.com/v15.0/{ig_user_id}/media_publish"
        publish_params = {
            'access_token': access_token,
            'creation_id': creation_id
        }

        publish_response = requests.post(publish_url, data=publish_params).json()
        return publish_response
    except Exception as e:
        print(f"Error uploading video to Instagram: {e}")
        return {"error": str(e)}

# Example usage for Instagram
ig_caption = text_quote
ig_response = upload_video_to_instagram(video_file_path, ig_caption, IG_ACCESS_TOKEN, IG_USER_ID)

if 'id' in ig_response:
    print('Video uploaded and published to Instagram successfully!')
    print('Response:', ig_response)
else:
    print('Failed to upload and publish video to Instagram.')
    print('Response:', ig_response)

def get_authenticated_service():
    credentials = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    credentials.refresh(Request())
    return build('youtube', 'v3', credentials=credentials)

def upload_video_to_youtube(video_file_path, title, description, tags, category_id, privacy_status):
    try:
        youtube = get_authenticated_service()

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True)

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = request.execute()
        print(f"Video uploaded to YouTube: {response['id']}")
        return response
    except Exception as e:
        print(f"Error uploading video to YouTube: {e}")
        return {"error": str(e)}

# Example usage for YouTube
youtube_title = shorten(text_quote, width=90, placeholder="...")
youtube_description = "https://amzn.to/4cv2MXh" +  text_quote
youtube_tags = ['cats', 'facts']
youtube_category_id = '22'  # YouTube category ID
youtube_privacy_status = 'public'

response = upload_video_to_youtube(video_file_path, youtube_title, youtube_description, youtube_tags, youtube_category_id, youtube_privacy_status)

if 'id' in response:
    print('Video uploaded to YouTube successfully!')
    print('Response:', response)
else:
    print('Failed to upload video to YouTube.')
    print('Response:', response)
