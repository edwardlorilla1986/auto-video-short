import os
import requests
import json
import urllib.request
import ast
from random import randint
from os import environ
from dotenv import load_dotenv

# Load environment constants
load_dotenv(".env")

VIDEOURL = environ["VIDEOURL"]
AUTH_TOKEN = json.loads(environ["AUTH_TOKEN"])  # Use json.loads instead of ast.literal_eval for JSON
VIDEO_NAME = environ["VIDEO_NAME"]

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

    # Download the video file
    try:
        urllib.request.urlretrieve(videoLink, f"output/{VIDEO_NAME}")
        print(f"Video successfully downloaded to output/{VIDEO_NAME}")
    except Exception as e:
        print(f"Error downloading video: {e}")
