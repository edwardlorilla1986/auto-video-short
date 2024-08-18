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

    # Modify the model's generation config
    model.config.use_cache = False
    model.config.pad_token_id = processor.tokenizer.eos_token_id

    # Generate the audio output
    audio = model.generate(
        **inputs,
        do_sample=True,
        max_new_tokens=256,
        temperature=0.7,
        no_repeat_ngram_size=3
    )

    # Save the audio to a file
    wavfile.write(f"output/{AUDIO}.wav", rate=model.config.sample_rate, data=audio.cpu().numpy().squeeze())

# Print the model's config to check
print(model.config)
