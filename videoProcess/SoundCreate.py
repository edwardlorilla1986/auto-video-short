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

    # Ensure attention_mask is created
    if 'attention_mask' not in inputs:
        inputs['attention_mask'] = torch.ones_like(inputs['input_ids'])

    # Set generation parameters
    generation_config = model.generation_config
    generation_config.pad_token_id = processor.tokenizer.eos_token_id
    generation_config.max_new_tokens = 256

    # Generate the audio output
    with torch.no_grad():
        audio = model.generate(
            **inputs,
            generation_config=generation_config
        )

    # Save the audio to a file
    wavfile.write(f"output/{AUDIO}.wav", rate=model.config.sample_rate, data=audio.cpu().numpy().squeeze())

    # Print debug information
    print("Inputs:", inputs)
    print("Generation Config:", generation_config)
