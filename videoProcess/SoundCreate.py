import subprocess
from os import environ
from dotenv import load_dotenv

# Load environment constants
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    # Define the Espeak voice. For Mbrola voices, use a format like "mb-en1" for English Mbrola voice 1.
    voice = "mb-en1"
    
    # Output file path
    output_file = f"output/{AUDIO}"
    
    # Generate speech with Espeak and save it as a WAV file
    subprocess.run([
        "espeak",
        "-v", voice,            # Specify the voice
        quote,                  # The text to synthesize
        "-w", output_file       # Output to the specified WAV file
    ])
    
    print(f"Audio saved to {output_file}")
