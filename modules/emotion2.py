import pyttsx3
from transformers import pipeline
import json

# Load emotion model
emotion_model_text = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion")

# Emotion to emoji mapping
emotion_to_emoji = {
    "admiration": "👏",
    "amusement": "😂",
    "anger": "😡",
    "annoyance": "😒",
    "approval": "👍",
    "caring": "🤗",
    "confusion": "😕",
    "curiosity": "🤔",
    "desire": "😍",
    "disappointment": "😞",
    "disapproval": "👎",
    "disgust": "🤢",
    "embarrassment": "😳",
    "excitement": "🤩",
    "fear": "😨",
    "gratitude": "🙏",
    "grief": "😭",
    "joy": "😊",
    "love": "❤",
    "nervousness": "😬",
    "optimism": "🌟",
    "pride": "😌",
    "realization": "💡",
    "relief": "😌",
    "remorse": "😔",
    "sadness": "😢",
    "surprise": "😲",
    "neutral": "😐",
    "default": "🙂"
}

# Updated emotion to voice settings mapping
emotion_to_voice = {
    "admiration": {"rate": 160, "volume": 1.2, "voice_index": 1},  # Warm, medium-fast, female
    "amusement": {"rate": 180, "volume": 1.5, "voice_index": 1},   # Fast, lively, female
    "anger": {"rate": 250, "volume": 1.1, "voice_index": 0},       # Fast, loud, male
    "annoyance": {"rate": 120, "volume": 0.8, "voice_index": 0},   # Slow, slightly loud, male
    "approval": {"rate": 150, "volume": 1.1, "voice_index": 1},    # Medium, warm, female
    "caring": {"rate": 140, "volume": 1.0, "voice_index": 1},      # Soft, warm, female
    "confusion": {"rate": 130, "volume": 0.9, "voice_index": 0},   # Slow, uncertain, male
    "curiosity": {"rate": 160, "volume": 1.0, "voice_index": 1},   # Medium, inquisitive, female
    "desire": {"rate": 150, "volume": 1.3, "voice_index": 1},      # Medium, soft, female
    "disappointment": {"rate": 100, "volume": 0.6, "voice_index": 0},  # Slow, soft, male
    "disapproval": {"rate": 110, "volume": 0.8, "voice_index": 0},     # Slow, firm, male
    "disgust": {"rate": 100, "volume": 0.7, "voice_index": 0},         # Slow, low tone, male
    "embarrassment": {"rate": 120, "volume": 0.6, "voice_index": 1},   # Hesitant, soft, female
    "excitement": {"rate": 180, "volume": 1.5, "voice_index": 1},      # Fast, enthusiastic, female
    "fear": {"rate": 150, "volume": 0.8, "voice_index": 1},            # Medium-fast, uncertain, female
    "gratitude": {"rate": 140, "volume": 1.0, "voice_index": 1},       # Warm, soft, female
    "grief": {"rate": 90, "volume": 0.6, "voice_index": 0},            # Slow, quiet, male
    "joy": {"rate": 170, "volume": 1.5, "voice_index": 1},             # Fast, happy, female
    "love": {"rate": 150, "volume": 1.3, "voice_index": 1},            # Medium, warm, female
    "nervousness": {"rate": 180, "volume": 0.9, "voice_index": 1},     # Fast, shaky, female
    "optimism": {"rate": 160, "volume": 1.2, "voice_index": 1},        # Medium-fast, cheerful, female
    "pride": {"rate": 140, "volume": 1.1, "voice_index": 0},           # Slow, confident, male
    "realization": {"rate": 150, "volume": 1.0, "voice_index": 1},     # Medium, clear, female
    "relief": {"rate": 120, "volume": 0.9, "voice_index": 1},          # Slow, soft, female
    "remorse": {"rate": 100, "volume": 0.6, "voice_index": 0},         # Slow, quiet, male
    "sadness": {"rate": 110, "volume": 0.6, "voice_index": 0},          # Slow, quiet, male
    "surprise": {"rate": 200, "volume": 1.5, "voice_index": 1},        # Fast, enthusiastic, female
    "neutral": {"rate": 150, "volume": 1.0, "voice_index": 0},         # Default, balanced, male
    "default": {"rate": 150, "volume": 1.0, "voice_index": 0}          # Fallback, balanced, male
}

# Function to detect emotion from text
def emotion_det_text(text):
    results = emotion_model_text(text)
    detected_emotion = results[0]["label"]
    emoji = emotion_to_emoji.get(detected_emotion, emotion_to_emoji["default"])
    
    response = {
        "type": "text",
        "emotion": detected_emotion,
        "emoji": emoji
    }
    print(json.dumps(response, indent=4))
    return response

# Function to convert text to speech with emotion and save to file
def text_to_emotion_speech(text, emotion, output_file):
    tts_engine = pyttsx3.init()
    
    # Get voice settings based on emotion
    voice_settings = emotion_to_voice.get(emotion, emotion_to_voice["default"])
    
    # Adjust TTS engine settings
    tts_engine.setProperty("rate", voice_settings["rate"])
    tts_engine.setProperty("volume", voice_settings["volume"])
    
    # Select voice (male/female)
    voices = tts_engine.getProperty('voices')
    voice_index = voice_settings["voice_index"]
    tts_engine.setProperty("voice", voices[voice_index].id)
    
    # Save speech to file
    tts_engine.save_to_file(text, output_file)
    tts_engine.runAndWait()

# Unified function to process text, generate emotional speech, and save audio
def emotion_detect(input_data, output_file, input_type="text"):
    if input_type == "text":
        emotion_response = emotion_det_text(input_data)
        detected_emotion = emotion_response["emotion"]
        
        # Generate speech with emotion and save it
        text_to_emotion_speech(input_data, detected_emotion, output_file)
        print(f"Audio saved to {output_file}")
        return emotion_response
    else:
        raise ValueError("Invalid input_type. Must be 'text'.")

# Example Usage
# text = "I am very sad i want to go home"
# emotion_det(text, input_type="text", output_file="sad_emotion.mp3")