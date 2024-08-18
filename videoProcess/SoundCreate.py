from bark import BarkModel
from os import environ
from dotenv import load_dotenv
import boto3
from random import randint

# Load environment constants
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    message = quote
    model = BarkModel.from_pretrained("suno/bark")
    audio = model.generate_audio(message)
    audio.save(f"output/{AUDIO}")
