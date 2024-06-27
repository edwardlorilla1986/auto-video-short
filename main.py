from os import environ
from dotenv import load_dotenv

# Load environment variables from .env file if running locally
load_dotenv(".env")

AUDIO_NAME = environ.get("AUDIO_NAME", "audio.mp3")
VIDEO_NAME = environ.get("VIDEO_NAME", "video.mp4")
FINAL_VIDEO = environ.get("FINAL_VIDEO", "final_video.mp4")

from videoProcess.Quote import get_quote
from videoProcess.SoundCreate import polly_audio, make_audio
from videoProcess.VideoDownload import download_video
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from textwrap import fill
from pyfiglet import Figlet

# Display a title using Figlet
fig_font = Figlet(font="slant", justify="left")
print(fig_font.renderText("Auto Video Short!!!"))

# Wait for user to start the program
input("Press ENTER/RETURN to start the program....")

try:
    # Get a quote and save it to a variable
    text_quote = get_quote()

    # Create the audio file from the quote
    # Uncomment polly_audio function and comment out make_audio function
    # if you have set up an AWS account and configured your local profile
    # polly_audio(text_quote)
    make_audio(text_quote)

    # Download the video clip from an API
    download_video()

    # Prepare the quote text for the video
    text_quote = fill(text_quote, width=30, fix_sentence_endings=True)

    # Set the resolution for the final video
    resolution = (1080, 1920)

    # Load the audio clip
    audio_clip = AudioFileClip(f"output/{AUDIO_NAME}")

    # Load the video clip, set the audio, loop the video, and resize
    video_clip = VideoFileClip(f"output/{VIDEO_NAME}", audio=False).set_audio(audio_clip).loop(duration=audio_clip.duration).resize(resolution)

    # Create a text clip with the quote
    fact_text = TextClip(text_quote, color='white', fontsize=50).set_position(('center', 1050))

    # Combine the video and text clips
    final = CompositeVideoClip([video_clip, fact_text], size=resolution)

    # Export the final video
    final.subclip(0, video_clip.duration).write_videofile(f"output/{FINAL_VIDEO}", fps=30, codec='libx264')

except Exception as e:
    print(f"OOPS Something went wrong!: {e}")
