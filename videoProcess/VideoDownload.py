import os
import requests
import json
import urllib.request
import ast
from random import randint
from os import environ
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from textwrap import fill
from PIL import Image

# Load environment constants
load_dotenv(".env")

VIDEOURL = environ["VIDEOURL"]
AUTH_TOKEN = json.loads(environ["AUTH_TOKEN"])  # Use json.loads instead of ast.literal_eval for JSON
VIDEO_NAME = environ["VIDEO_NAME"]
AUDIO_NAME = environ["AUDIO_NAME"]
FINAL_VIDEO = environ["FINAL_VIDEO"]

def download_video():
    # Create random number between 0 and 49
    random_index = randint(0, 49)
    
    # Ensure output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')

    # Request stored in response variable
    response = requests.get(VIDEOURL, headers=AUTH_TOKEN)

    # Check if the response was successful
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)
        return

    # Format the response 
    format_response = response.text
    print("Response JSON:", format_response)  # Print the JSON response for debugging

    # Parse json 
    parse_json = json.loads(format_response)

    # Check if 'videos' key exists in the parsed JSON
    if 'videos' not in parse_json:
        print("Error: 'videos' key not found in the response")
        return

    # Grab the external video link
    videoLink = parse_json['videos'][random_index]['video_files'][0]['link']
    print(f"Downloading video from: {videoLink}")

    # Download the video file using requests
    try:
        video_response = requests.get(videoLink, stream=True)
        video_response.raise_for_status()  # Raise an exception for HTTP errors

        with open(f"output/{VIDEO_NAME}", 'wb') as file:
            for chunk in video_response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Video successfully downloaded to output/{VIDEO_NAME}")
    except Exception as e:
        print(f"Error downloading video: {e}")

def create_final_video():
    # Prepare the quote text for the video
    quote = "This is a sample quote for generating speech."
    text_quote = fill(quote, width=30, fix_sentence_endings=True)
    resolution = (1080, 1920)

    # Load the audio clip
    audio_clip = AudioFileClip(f"output/{AUDIO_NAME}")

    try:
        video_clip = VideoFileClip(f"output/{VIDEO_NAME}", audio=False).set_audio(audio_clip).loop(duration=audio_clip.duration).resize(resolution)
        fact_text = TextClip(text_quote, color='white', fontsize=50).set_position(('center', 1050))
        final = CompositeVideoClip([video_clip, fact_text], size=resolution)
        final.subclip(0, video_clip.duration).write_videofile(f"output/{FINAL_VIDEO}", fps=30, codec='libx264')
        print(f"Final video successfully created at output/{FINAL_VIDEO}")
    except Exception as e:
        print(f"Error processing video: {e}")

