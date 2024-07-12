import os
import requests
import time
from os import environ
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from textwrap import fill, shorten
from pyfiglet import Figlet

# Load environment variables from .env file if running locally
load_dotenv(".env")

# Constants and configuration
CLIENT_ID = environ.get("CLIENT_ID")
CLIENT_SECRET = environ.get("CLIENT_SECRET")
REFRESH_TOKEN = environ.get("REFRESH_TOKEN")
AUDIO_NAME = environ.get("AUDIO_NAME", "audio.mp3")
VIDEO_NAME = environ.get("VIDEO_NAME", "video.mp4")
FINAL_VIDEO = environ.get("FINAL_VIDEO", "final_video.mp4")
PAGE_ID = environ.get("PAGE_ID")
PAGE_ACCESS_TOKEN = environ.get("PAGE_ACCESS_TOKEN")

# Ensure output directory exists
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Display a title using Figlet
fig_font = Figlet(font="slant", justify="left")
print(fig_font.renderText("Auto Video Short!!!"))

# Prepare the quote text for the video
def get_quote():
    # Placeholder function to get a quote
    return "This is a sample quote."

def make_audio(text_quote):
    # Placeholder function to create audio from text
    pass

def download_video():
    # Placeholder function to download a video
    pass

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

def initialize_upload_session(page_id, page_access_token):
    init_url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    init_params = {
        'upload_phase': 'start',
        'access_token': page_access_token
    }
    init_response = requests.post(init_url, json=init_params).json()
    if 'video_id' in init_response and 'upload_url' in init_response:
        return init_response['video_id'], init_response['upload_url']
    else:
        raise Exception(f"Failed to initiate upload: {init_response}")

def upload_video_in_chunks(upload_url, video_file_path, page_access_token):
    chunk_size = 1024 * 1024 * 4  # 4MB chunks
    file_size = os.path.getsize(video_file_path)
    
    start_offset = 0
    while start_offset < file_size:
        with open(video_file_path, 'rb') as video_file:
            video_file.seek(start_offset)
            video_chunk = video_file.read(chunk_size)
            headers = {
                'Authorization': f'OAuth {page_access_token}',
                'offset': str(start_offset),
                'file_size': str(file_size),
                'Content-Type': 'application/octet-stream'
            }
            response = requests.post(upload_url, headers=headers, data=video_chunk)
            upload_response = response.json()

            if 'start_offset' not in upload_response:
                if 'debug_info' in upload_response and upload_response['debug_info'].get('type') == 'PartialRequestError':
                    print(f"Partial request error: {upload_response['debug_info']['message']}. Retrying...")
                    continue
                else:
                    raise Exception(f"Error during upload: {upload_response}")

            start_offset = int(upload_response['start_offset'])

def check_upload_status(video_id, page_access_token):
    status_url = f"https://graph.facebook.com/v20.0/{video_id}?fields=status&access_token={page_access_token}"
    status_response = requests.get(status_url).json()
    if 'status' in status_response:
        return status_response['status']
    else:
        raise Exception(f"Failed to check upload status: {status_response}")

def finalize_upload_session(page_id, video_id, page_access_token, caption):
    while True:
        status = check_upload_status(video_id, page_access_token)
        video_status = status.get('video_status')
        if video_status == 'ready':
            finish_url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
            finish_params = {
                'access_token': page_access_token,
                'upload_phase': 'finish',
                'video_id': video_id,
                'title': caption,
                'description': caption,
                'video_state': 'PUBLISHED'
            }
            finish_response = requests.post(finish_url, data=finish_params).json()
            if 'success' in finish_response and finish_response['success']:
                return finish_response
            else:
                raise Exception(f"Failed to finalize upload: {finish_response}")
        elif video_status == 'processing':
            print("Video is still processing. Checking again in 10 seconds...")
            time.sleep(10)
        else:
            raise Exception(f"Unexpected video status: {status}")

# Example usage
video_title = text_quote
video_description = text_quote
video_file_path = f"{output_dir}/{FINAL_VIDEO}"

try:
    video_id, upload_url = initialize_upload_session(PAGE_ID, PAGE_ACCESS_TOKEN)
    upload_video_in_chunks(upload_url, video_file_path, PAGE_ACCESS_TOKEN)
    response = finalize_upload_session(PAGE_ID, video_id, PAGE_ACCESS_TOKEN, video_description)
    print('Video uploaded successfully as a reel on Facebook!')
    print('Response:', response)
except Exception as e:
    print('Failed to upload video as a reel on Facebook.')
    print('Error:', e)
