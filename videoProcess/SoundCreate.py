
import torch
from transformers import AutoProcessor, BarkModel
import scipy.io.wavfile as wavfile
from os import environ
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]
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
expressions = [ "", ""]

def insert_random_expressions(text, expressions, num_insertions=2):
    words = text.split()
    for _ in range(num_insertions):
        index = random.randint(0, len(words) - 1)
        words.insert(index, random.choice(expressions))
    return " ".join(words)

# Modify the text_prompt by inserting random expression
def split_text_into_chunks(text, max_length):
    """
    Split text into chunks that fit within the model's token limit.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(processor(" ".join(current_chunk), return_tensors="pt")['input_ids'][0]) > max_length:
            # Add the chunk without the last word which made it exceed the max length
            chunks.append(" ".join(current_chunk[:-1]))
            # Start a new chunk with the last word
            current_chunk = [word]
    
    # Add the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def make_audio(quote):
    """
    Generate audio from a quote by splitting the text into chunks.
    """
    # Example expressions to add
    expressions = [""]

    # Insert random expressions into the text
    processed_text = insert_random_expressions(quote, expressions)

    # Split the text into chunks that fit within the model's token limit
    max_length = 512  # Adjust this based on the model's token limit
    chunks = split_text_into_chunks(processed_text, max_length)

    # Initialize an empty array to store the full audio
    full_audio = np.array([])

    # Generate audio for each chunk and concatenate the results
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}")

        # Tokenize the chunk
        inputs = processor(text=chunk, return_tensors="pt", padding=True, truncation=True)

        # Ensure attention_mask is explicitly set
        inputs['attention_mask'] = inputs['input_ids'].ne(processor.tokenizer.pad_token_id).long()

        # Move inputs to the same device as the model
        inputs = {key: value.to(device) for key, value in inputs.items()}

        # Generate audio with an explicit `pad_token_id`
        audio_array = model.generate(
            input_ids=inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            pad_token_id=processor.tokenizer.pad_token_id
        )

        # Convert the generated audio to numpy and concatenate
        audio_array = audio_array.cpu().numpy().squeeze()

        # Append the audio of this chunk to the full audio array
        full_audio = np.concatenate([full_audio, audio_array])

    # Specify the sample rate
    sample_rate = 24000  # 24000 Hz is a common sample rate for audio

    # Save the concatenated audio output as a .wav file
    wavfile.write(f"output/full_audio.wav", rate=sample_rate, data=full_audio)

    print("Full audio generated and saved as 'full_audio.wav'.")
