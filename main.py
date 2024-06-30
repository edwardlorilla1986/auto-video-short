import os
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
from email.mime.base import MIMEBase
from email import encoders
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

def send_email(subject, body, to, file_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(file_path, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    text = msg.as_string()
    server.sendmail(EMAIL_USER, to, text)
    server.quit()
    print(f"Email sent to {to} with attachment {file_path}")

video_title = 'Your Video Title'
video_description = 'Your Video Description'
video_file_path = f"{output_dir}/{FINAL_VIDEO}"
PAGE_ID = "332087273320790"
PAGE_ACCESS_TOKEN = "EAAWuCPnPZAZA4BO25aybcV45kgkw7oGHr4srFJD7L3TzXT7ZBHvzHoxk1BClkvZCvRo25pY4ZBOavHcTPUhId0ljdNks81tqpuYfnXC6COpiDjSSNOY4SrwWP8HstzI4ytXdqq7W9ERfJenhfLBcOXPdNPpzZBFe5AV0pYUIA1ZAokUTnXfBpDrsTnKPL5vbNejZCtLo3A1o2LyOwyJkzeILb8xU4mVX6jXlpgZDZD"
# URL for uploading video
url = f'https://graph.facebook.com/v11.0/{PAGE_ID}/videos'

# Open the video file
with open(video_file_path, 'rb') as video_file:
    # Prepare the payload
    payload = {
        'title': video_title,
        'description': video_description,
        'access_token': PAGE_ACCESS_TOKEN
    }
    
    # Prepare the files
    files = {
        'file': video_file
    }
    
    # Make the request to upload the video
    response = requests.post(url, data=payload, files=files)
    
    # Check the response
    if response.status_code == 200:
        print('Video uploaded successfully!')
        print('Response:', response.json())
    else:
        print('Failed to upload video.')
        print('Response:', response.json())
# Send the final video as an email attachment
#send_email(
#    subject="Your Auto Video Short",
#    body="Please find the attached video.",
#    to=EMAIL_TO,
#    file_path=final_video_path
#)
