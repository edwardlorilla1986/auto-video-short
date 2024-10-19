
import torch
from transformers import AutoProcessor, BarkModel, AutoTokenizer, AutoModelForCausalLM
import scipy.io.wavfile as wavfile
from os import environ
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]
tokenizer = AutoTokenizer.from_pretrained("huggyllama/llama-7b")
model = AutoModelForCausalLM.from_pretrained("huggyllama/llama-7b")
prompt = "Generate an interesting fact about cats."
# Initialize the processor and model
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
def make_audio(quote):
    _inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=50)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    inputs = processor(text=insert_random_expressions(generated_text, expressions)
, voice_preset=voice_preset, return_tensors="pt")
    
    # Generate the attention mask
    attention_mask = inputs['input_ids'].ne(processor.tokenizer.pad_token_id).long()
    inputs['attention_mask'] = attention_mask
    
    # Move inputs to the same device as the model
    for key in inputs:
        inputs[key] = inputs[key].to(device)
    
    # Generate the audio output with the attention mask and pad token id
    audio_array = model.generate(input_ids=inputs['input_ids'], attention_mask=attention_mask, pad_token_id=processor.tokenizer.eos_token_id)
    audio_array = audio_array.cpu().numpy().squeeze()
    
    # Specify a default sample rate
    sample_rate = 24000  # Use 24000 Hz as a common sample rate for audio
    wavfile.write(f"output/{AUDIO}", rate=sample_rate, data=audio_array)
