import torch
from transformers import AutoProcessor, BarkModel
import scipy.io.wavfile as wavfile
import numpy as np
from os import environ
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

# Initialize processor and model
processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")

# Optionally move the model to CUDA if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Voice preset (try other options if desired)
voice_preset = "v2/en_speaker_6"

# Define text prompt
text_prompt = """
Hi, my name is Prateek, welcome you all. Today we are going to discuss olivine crystal, so let's start.
"""

# List of optional expressions to insert
expressions = ["wow", "uh", "hmm", "interesting"]

def insert_random_expressions(text, expressions, num_insertions=2):
    words = text.split()
    for _ in range(num_insertions):
        index = random.randint(0, len(words) - 1)
        words.insert(index, random.choice(expressions))
    return " ".join(words)

def split_text_into_chunks(text, max_length):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(processor(" ".join(current_chunk), return_tensors="pt")['input_ids'][0]) > max_length:
            chunks.append(" ".join(current_chunk[:-1]))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def make_audio(quote):
    processed_text = insert_random_expressions(quote, expressions)
    max_length = 512  # Adjust based on the model's limit
    chunks = split_text_into_chunks(processed_text, max_length)

    full_audio = np.array([])

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}")

        inputs = processor(text=chunk, return_tensors="pt")
        attention_mask = inputs['input_ids'].ne(processor.tokenizer.pad_token_id).long()
        inputs['attention_mask'] = attention_mask

        inputs = {key: value.to(device) for key, value in inputs.items()}

        try:
            audio_array = model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                pad_token_id=processor.tokenizer.pad_token_id
            )

            audio_array = audio_array.cpu().numpy().squeeze()
            full_audio = np.concatenate([full_audio, audio_array])

        except Exception as e:
            print(f"Error generating audio for chunk {i + 1}: {e}")

    sample_rate = 24000
    wavfile.write(f"output/{AUDIO}", rate=sample_rate, data=full_audio.astype(np.float32))
