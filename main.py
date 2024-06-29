import os
from os import environ
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, vfx
from moviepy.video.tools.drawing import color_gradient
from textwrap import fill
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
    file.write(text_quote)
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
    video_clip = (VideoFileClip(video_path, audio=False)
                  .set_audio(audio_clip)
                  .loop(duration=audio_clip.duration)
                  .resize(resolution))

    # Apply a slight Gaussian blur to the video
    blurred_bg = video_clip.fx(vfx.all.gaussian_blur, sigma=3)

    # Create a text clip with the quote
    fact_text = (TextClip(text_quote, fontsize=50, color='white', font='Helvetica-Bold', 
                          kerning=2, interline=1.5, align='center', size=(resolution[0]*0.8, None))
                 .set_position(('center', 'center'))
                 .set_duration(video_clip.duration)
                 .crossfadein(1)
                 .crossfadeout(1))

    # Add a subtle animation to the text
    animated_text = fact_text.set_position(lambda t: ('center', 'center' + 20*np.sin(t)))

    # Create a semi-transparent gradient overlay
    gradient = (color_gradient(size=resolution, 
                                  colors=[(0,0,0,0.7), (0,0,0,0.3)], 
                                  start_pos=(0,0), 
                                  end_pos=(0,1080))
                .set_duration(video_clip.duration))

    # Create a watermark
    watermark = (TextClip("EdwardLanceLorilla", fontsize=30, color='white', font='Arial-Bold')
                 .set_position(('right', 'bottom'))
                 .set_duration(video_clip.duration)
                 .set_opacity(0.5))

    # Compose the final video
    final = CompositeVideoClip([blurred_bg, gradient, animated_text, watermark])
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

# Send the final video as an email attachment
#send_email(
#    subject="Your Auto Video Short",
#    body="Please find the attached video.",
#    to=EMAIL_TO,
#    file_path=final_video_path
#)
