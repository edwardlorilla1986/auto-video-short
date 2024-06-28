import os
import pickle
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from os import environ
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from textwrap import fill
from pyfiglet import Figlet
from videoProcess.Quote import get_quote
from videoProcess.SoundCreate import make_audio
from videoProcess.VideoDownload import download_video
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables from .env file if running locally
load_dotenv(".env")

AUDIO_NAME = environ.get("AUDIO_NAME", "audio.mp3")
VIDEO_NAME = environ.get("VIDEO_NAME", "video.mp4")
FINAL_VIDEO = environ.get("FINAL_VIDEO", "final_video.mp4")
BLOG_EMAIL = environ.get("BLOG_EMAIL")  # Your Blogger posting email address
EMAIL_USER = environ.get("EMAIL_USER")  # Your email address
EMAIL_PASS = environ.get("EMAIL_PASS")  # Your email password
REFRESH_TOKEN = environ.get("REFRESH_TOKEN")  # Your refresh token
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

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
    fact_text = TextClip(text_quote, color='white', fontsize=50).set_position(('center', 1050))

    # Combine the video and text clips
    final = CompositeVideoClip([video_clip, fact_text], size=resolution)

    # Export the final video
    final_video_path = f"{output_dir}/{FINAL_VIDEO}"
    final.subclip(0, video_clip.duration).write_videofile(final_video_path, fps=30, codec='libx264')
    print(f"Final video successfully created at {final_video_path}")
except Exception as e:
    print(f"Error processing video: {e}")



# Function to send email with video link
def send_email(subject, body, to):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    text = msg.as_string()
    server.sendmail(EMAIL_USER, to, text)
    server.quit()
    print(f"Email sent to {to}")

# Send the email to Blogger with the YouTube video link
email_body = f"""
<h2>Your Auto Video Short</h2>
<p>Here is your auto-generated video:</p>
"""

send_email(
    subject="Auto Video Short",
    body=email_body,
    to=BLOG_EMAIL
)
