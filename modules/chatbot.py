from huggingface_hub import InferenceClient
import google.generativeai as genai
import base64
import re
from io import BytesIO
from PIL import Image

hf_client = InferenceClient(api_key="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")

genai.configure(api_key="AIzaSyAzRlbHISAwL7ytMoSb4M9VOxn9cFDlGhU")
genai_model = genai.GenerativeModel("gemini-1.5-flash")


def load_local_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def chat_with_image(conversation, model="meta-llama/Llama-3.2-11B-Vision-Instruct"):
    completion = hf_client.chat.completions.create(
        model=model,
        messages=conversation,
        max_tokens=500,
    )
    return completion.choices[0].message


def chat_with_text(conversation):
    user_query = conversation[-1]["content"] if conversation else "Hello"
    response = genai_model.generate_content(contents=[{"text": user_query}])
    return response.text

def get_image_mime_type(image_data):
    try:
        img = Image.open(BytesIO(image_data))
        mime_type = img.format.lower()
        return mime_type
    except Exception as e:
        return None

def anugrah_Vision_Llama_v1(image=None, text_query=None, conversation=None):
    if not conversation:
        conversation = []

    if image:
        image_data = image.read()
        mime_type = get_image_mime_type(image_data)

        if mime_type is None:
            return f"Unsupported image format.{mime_type}"
        base64_image = base64.b64encode(image_data).decode('utf-8')
        image_url = f"data:image/{mime_type};base64,{base64_image}"
        # print(image_url)
        conversation.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text_query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        })

        response = chat_with_image(conversation)
        return response["content"]

    elif text_query:
        conversation.append({
            "role": "user",
            "content": text_query
        })

        response = chat_with_text(conversation)
        return response

    else:
        return "Please provide either an image or a text query."

