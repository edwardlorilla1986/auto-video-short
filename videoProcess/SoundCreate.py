from transformers import AutoProcessor, BarkModel
from os import environ
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    processor = AutoProcessor.from_pretrained("suno/bark")
    model = BarkModel.from_pretrained("suno/bark")
    
    # Process the text input
    inputs = processor(text=quote, return_tensors="pt")
    
    # Generate the audio output
    audio = model.generate(**inputs, pad_token_id=processor.tokenizer.eos_token_id)
    
    # Save the audio to a file
    with open(f"output/{AUDIO}.wav", "wb") as f:
        f.write(audio)
