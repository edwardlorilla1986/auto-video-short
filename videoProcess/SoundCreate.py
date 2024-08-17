from bark import SAMPLE_RATE, generate_audio, preload_models
from os import environ
from dotenv import load_dotenv
import boto3
from random import randint
import numpy as np
from scipy.io.wavfile import write

# Load environment constants
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

# Preload Bark models
preload_models()

def make_audio(quote):
    # Generate audio using Bark
    speech_array = generate_audio(quote)
    
    # Convert to proper format and save the file
    output_path = f"output/{AUDIO}"
    write(output_path, SAMPLE_RATE, np.array(speech_array * 32767, dtype=np.int16))
    print(f"Audio saved to {output_path}")
