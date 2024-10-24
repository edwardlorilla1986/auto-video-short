
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
from PIL import Image, ImageDraw, ImageFont
import math
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

        video_path = f"output/{VIDEO_NAME}"
        with open(video_path, 'wb') as file:
            for chunk in video_response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Video successfully downloaded to {video_path}")
        if not os.path.exists(video_path):
            print(f"Error: {video_path} could not be found after download")
    except Exception as e:
        print(f"Error downloading video: {e}")

def create_text_image(text, font_path="arial.ttf", font_size=50, image_size=(1080, 1920), text_color="white", bg_color="black"):
    # Create a blank image with the specified background color
    image = Image.new('RGB', image_size, color=bg_color)
    
    # Initialize the drawing context
    draw = ImageDraw.Draw(image)
    
    # Load the font
    font = ImageFont.truetype(font_path, font_size)
    
    # Wrap the text to fit the image width
    wrapped_text = textwrap.fill(text, width=40)
    
    # Calculate text size and position
    text_width, text_height = draw.textsize(wrapped_text, font=font)
    position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)
    
    # Draw the text on the image
    draw.text(position, wrapped_text, font=font, fill=text_color)
    
    return image

def create_final_video(quote):
    resolution = (1080, 1920)

    # Load the audio clip
    audio_clip = AudioFileClip(f"output/{AUDIO_NAME}")

    video_path = f"output/{VIDEO_NAME}"
    if not os.path.exists(video_path):
        print(f"Error: {video_path} could not be found before processing")
        return

    try:
        # Load the video clip without audio
        video_clip = VideoFileClip(video_path, audio=False)

        # Calculate how many times the video needs to loop to match the audio duration
        video_duration = video_clip.duration
        audio_duration = audio_clip.duration
        loop_count = int(audio_duration // video_duration) + 1

        # Loop the video and set it to match the audio duration
        looped_video_clip = video_clip.loop(n=loop_count).subclip(0, audio_duration).set_audio(audio_clip).resize(resolution)

        # Split the text into chunks for sequential display
        text_chunks = textwrap.wrap(quote, width=40)
        chunk_duration = audio_duration / len(text_chunks)

        # Create ImageClips from text chunks
        text_clips = []
        for i, chunk in enumerate(text_chunks):
            img = create_text_image(chunk, image_size=resolution)
            text_clip = ImageClip(img).set_duration(chunk_duration).set_start(i * chunk_duration)
            text_clips.append(text_clip)

        # Combine the video and text clips into the final clip
        final = CompositeVideoClip([looped_video_clip] + text_clips, size=resolution)

        # Export the final video
        final.write_videofile(f"output/{FINAL_VIDEO}", fps=30, codec='libx264')
        print(f"Final video successfully created at output/{FINAL_VIDEO}")
    except Exception as e:
        print(f"Error processing video: {e}")
