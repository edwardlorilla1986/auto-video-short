from transformers import AutoProcessor, BarkModel
from os import environ
from dotenv import load_dotenv
import torch

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    processor = AutoProcessor.from_pretrained("suno/bark")
    model = BarkModel.from_pretrained("suno/bark")
    
    # Process the text input
    inputs = processor(text=quote, return_tensors="pt", padding=True)
    
    # Manually set the attention mask
    attention_mask = torch.ones_like(inputs['input_ids'], dtype=torch.long)
    
    # Generate the audio output with attention_mask and pad_token_id
    audio = model.generate(**inputs, attention_mask=attention_mask, pad_token_id=processor.tokenizer.eos_token_id)
    
    # Save the audio to a file
    with open(f"output/{AUDIO}.wav", "wb") as f:
        f.write(audio)

make_audio("Hello, this is a test of the Bark model.")
