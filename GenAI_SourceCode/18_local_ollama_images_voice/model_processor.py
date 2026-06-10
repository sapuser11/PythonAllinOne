import ollama
from PIL import Image
import speech_recognition as sr
from pathlib import Path

def process_image(image_path):
    """Process image and get description from Ollama"""
    try:
        # Read image as bytes
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        response = ollama.chat(
            model='llama3.2-vision',  # Use vision model
            messages=[{
                'role': 'user',
                'content': 'Describe this image in detail.',
                'images': [image_bytes]
            }]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error processing image: {str(e)}"

def process_audio(audio_path):
    """Convert speech to text and process with Ollama"""
    recognizer = sr.Recognizer()
    
    try:
        # Convert audio to text
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        
        # Process with Ollama
        response = ollama.chat(
            model='llama3.1',
            messages=[{
                'role': 'user',
                'content': f'The user said: "{text}". Please respond appropriately.'
            }]
        )
        
        return {
            'transcription': text,
            'response': response['message']['content']
        }
    except Exception as e:
        return {'error': str(e)}

def chat_with_text(text):
    """Simple text chat with Ollama"""
    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[{
                'role': 'user',
                'content': text
            }]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"