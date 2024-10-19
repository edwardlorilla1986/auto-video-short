import torch
from transformers import AutoProcessor, BarkModel
import scipy.io.wavfile as wavfile
import numpy as np
from os import environ
from dotenv import load_dotenv
import random
import nltk 
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
expressions = [""]

def insert_random_expressions(text, expressions, num_insertions=2):
    words = text.split()
    for _ in range(num_insertions):
        index = random.randint(0, len(words) - 1)
        words.insert(index, random.choice(expressions))
    return " ".join(words)

 # For splitting text into sentences

nltk.download('punkt')

def split_text_into_sentences(text, max_length):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
            
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def make_audio(quote):
    processed_text = insert_random_expressions(quote, expressions)
    max_length = 512  # Adjust based on the model's limit
    chunks = split_text_into_sentences(processed_text, max_length)

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

            # Introduce a small pause of silence (e.g., 1 second at 24000 Hz)
            pause_duration = 1 * 24000  # 1 second pause
            silence = np.zeros(pause_duration)

            # Concatenate the generated audio and silence to the final output
            full_audio = np.concatenate([full_audio, audio_array, silence])

        except Exception as e:
            print(f"Error generating audio for chunk {i + 1}: {e}")

    sample_rate = 24000
    wavfile.write(f"output/{AUDIO}", rate=sample_rate, data=full_audio.astype(np.float32))
