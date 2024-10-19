import torch
from scipy.io import wavfile
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import numpy as np

# Define device and load models
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = AutoProcessor.from_pretrained("facebook/s2t-small-librispeech-asr")
model = AutoModelForSpeechSeq2Seq.from_pretrained("facebook/s2t-small-librispeech-asr").to(device)

def insert_random_expressions(text, expressions):
    """
    Insert random expressions like 'wow', 'haha' into the text.
    """
    words = text.split()
    for i in range(0, len(words), 5):  # Insert every 5 words for illustration
        words.insert(i, np.random.choice(expressions))
    return " ".join(words)

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


