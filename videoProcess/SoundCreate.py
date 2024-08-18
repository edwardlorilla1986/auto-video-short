from transformers import AutoProcessor, BarkModel
from os import environ
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")
AUDIO = environ["AUDIO_NAME"]

def make_audio(quote):
    # Load the processor and model from Hugging Face
    processor = AutoProcessor.from_pretrained("suno/bark")
    model = BarkModel.from_pretrained("suno/bark")
    
    # Process the text input
    inputs = processor(text=quote, return_tensors="pt", padding=True)
    
    # Manually set the attention mask
    inputs['attention_mask'] = inputs['input_ids'].ne(processor.tokenizer.pad_token_id).long()
    
    # Generate the audio output with the pad_token_id explicitly set
    audio = model.generate(**inputs, pad_token_id=processor.tokenizer.eos_token_id)
    
    # Save the audio to a file
    with open(f"output/{AUDIO}.wav", "wb") as f:
        f.write(audio)
