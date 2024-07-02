import os
import base64
import requests
from os import environ
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from textwrap import fill, shorten
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
EMAIL_USER = environ.get("EMAIL_USER")
EMAIL_PASS = environ.get("EMAIL_PASS")
EMAIL_TO = environ.get("EMAIL_TO")

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
    msg['Subject'] = text_quote

    html = f"""
    <html>
    <head>
        <style>
            .video-container {{
                position: relative;
                padding-bottom: 56.25%; /* 16:9 aspect ratio */
                padding-top: 25px;
                height: 0;
            }}
            .video-container video {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
            }}
        </style>
    </head>
    <body>
        <div class="video-container">
            <video controls>
                <source src="data:video/mp4;base64,{base64_video}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    </body>
    </html>
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
    subject="Your Auto Video Short",
    body="Please find the embedded video below.",
    to=EMAIL_TO,
    base64_video=base64_video
)
