from transformers import AutoProcessor, BarkModel
from os import environ
from dotenv import load_dotenv
import torch
import scipy.io.wavfile as wavfile

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    processor = AutoProcessor.from_pretrained("suno/bark")
    model = BarkModel.from_pretrained("suno/bark")

    # Process the text input
    inputs = processor(text=[quote], return_tensors="pt")

    # Ensure attention_mask is created and passed correctly
    if 'attention_mask' not in inputs:
        inputs['attention_mask'] = torch.ones_like(inputs['input_ids'])

    # Generate the audio output
    audio = model.generate(
        input_ids=inputs['input_ids'],
        attention_mask=inputs['attention_mask'],
        pad_token_id=processor.tokenizer.eos_token_id
    )

    # Save the audio to a file
    wavfile.write(f"output/{AUDIO}.wav", rate=model.config.sample_rate, data=audio.cpu().numpy().squeeze())
