import os
import subprocess
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
AUTH_TOKEN = ast.literal_eval(environ["AUTH_TOKEN"])
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
    print(AUTH_TOKEN)
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

def git_commit_and_push():
    try:
        # Add changes to Git
        subprocess.run(['git', 'add', 'main.py', 'videoProcess/VideoDownload.py', 'output/'], check=True)
        
        # Commit changes
        commit_message = "Add output directory with downloaded video file"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push changes to the remote repository
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("Changes pushed to GitHub successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running git command: {e}")
