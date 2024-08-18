from transformers import AutoProcessor, BarkModel
from os import environ
from dotenv import load_dotenv
import torch

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    # Load the processor and model from Hugging Face
    processor = AutoProcessor.from_pretrained("suno/bark")
    model = BarkModel.from_pretrained("suno/bark")
    
    # Process the text input
    inputs = processor(text=quote, return_tensors="pt", padding=True)
    
    # Generate the attention mask
    attention_mask = torch.ones(inputs.input_ids.shape, dtype=torch.long)
    
    # Generate the audio output
    audio = model.generate(**inputs, attention_mask=attention_mask)
    
    # Save the audio to a file
    with open(f"output/{AUDIO}.wav", "wb") as f:
        f.write(audio)
