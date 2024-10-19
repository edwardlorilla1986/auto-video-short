
from os import environ
from dotenv import load_dotenv
import boto3
from random import randint
from TTS.api import TTS
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    message = quote
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True, gpu=False)
    tts.tts_to_file(text="Hello, this is a test message.", file_path="f"output/{AUDIO}"")
