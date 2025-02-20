from transformers import pipeline
import json
from PIL import Image

emotion_model_text = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion")
emotion_model_image = pipeline("image-classification", model="microsoft/resnet-50") 


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
    "love": "❤️",
    "nervousness": "😬",
    "optimism": "🌟",
    "pride": "😌",
    "realization": "💡",
    "relief": "😌",
    "remorse": "😔",
    "sadness": "😢",
    "surprise": "😲",
    "neutral": "😐",
    "smiling": "😊",
    "laughing": "😂",
    "crying": "😭",
    "angry face": "😡",
    "fearful face": "😨",
    "surprised face": "😲",
    "neutral face": "😐",
    "happy face": "😊",
    "sad face": "😢",
    "disgusted face": "🤢",
    "confused face": "😕",
    "sleeping face": "😴",
    "worried face": "😟",
    "thinking face": "🤔",
    "shocked face": "😳",
    "relaxed face": "😌",
    "blushing face": "😊",
    "default": "🙂"
}


def emotion_det_text(text):
    results = emotion_model_text(text)
    detected_emotion = results[0]["label"]
    emoji = emotion_to_emoji.get(detected_emotion, "🙂")
    
    response = {
        "type": "text",
        "emotion": detected_emotion,
        "emoji": emoji
    }
    return response

def emotion_det_image(image_path):
    image = Image.open(image_path).convert("RGB")
    results = emotion_model_image(image)
    detected_emotion = results[0]["label"]
    emoji = emotion_to_emoji.get(detected_emotion, "🙂") 

    response = {
        "type": "image",
        "emotion": detected_emotion,
        "emoji": emoji
    }
    print(json.dumps(response, indent=4))
    return response


# def emotion_det(input_data, input_type="text"):
#     if input_type == "text":
#         return emotion_det_text(input_data)
#     elif input_type == "image":
#         return emotion_det_image(input_data)
#     else:
#         raise ValueError("Invalid input_type. Must be 'text' or 'image'.")

# text = "I am so happy today!"
# res1 = emotion_det(text, input_type="text")
# print(res1.get("emoji"))

# image_path = r'L:\My projects\Anugrah\image.png'
# res2 = emotion_det(image_path, input_type="image")
# print(res2.get("emoji"))