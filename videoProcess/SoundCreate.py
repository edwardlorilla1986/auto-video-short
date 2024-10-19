from gtts import gTTS
from os import environ
from dotenv import load_dotenv
import boto3
from random import randint

#load environment constants
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    message = quote
    speech = gTTS(message)
    speech.save(f"output/{AUDIO}")
