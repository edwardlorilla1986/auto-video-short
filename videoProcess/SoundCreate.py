import torch
from transformers import AutoProcessor, BarkModel
import scipy.io.wavfile as wavfile
from os import environ
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

# Initialize the processor and model
processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")

# Optionally move the model to CUDA if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Define the voice preset
voice_preset = "v2/en_speaker_6"

# Define the text prompt
text_prompt = """
Hi, my name is Prateek, welcome you all. Today we are going to discuss about olivine crystal, so let's start.
"""

# List of random expressions to insert
expressions = [ "[MAN]", "[WOMAN]"]

def insert_random_expressions(text, expressions, num_insertions=2):
    words = text.split()
    for _ in range(num_insertions):
        index = random.randint(0, len(words) - 1)
        words.insert(index, random.choice(expressions))
    return " ".join(words)

# Modify the text_prompt by inserting random expression
def make_audio(quote):
    print("123")
