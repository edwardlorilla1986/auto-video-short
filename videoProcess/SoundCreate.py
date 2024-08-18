from transformers import pipeline
import scipy.io.wavfile as wavfile
from os import environ
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    # Initialize the TTS pipeline
    synthesiser = pipeline("text-to-speech", "suno/bark")

    # Generate speech
    speech = synthesiser(quote, forward_params={"do_sample": True})

    # Save the audio output to a .wav file
    wavfile.write(f"output/{AUDIO}.wav", rate=speech["sampling_rate"], data=speech["audio"])
