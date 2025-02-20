from flask import Flask, jsonify, request, send_file, session
from flask_cors import CORS
from pytube import YouTube
from io import BytesIO
from PIL import Image

import subprocess
import traceback
import base64
import imghdr
import json
import io
import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from auth.generate_otp import generate_secure_otp

from web3Chatdapp.web3_chat_security import send_message, get_user_messages

from modules import translate_text
from modules import base64_transcribe
from modules import transliterate
from modules import generate_isl_videos
from modules import youtube_vide_to_sign
from modules import anugrah_Vision_Llama_v1
from modules import youtube_video_description
from modules import video_to_sign
from modules import emotion_det_text
from modules import emotion_detect
from modules import place_call


app = Flask(__name__)

CORS(app)

app.secret_key = '1234567890'

@app.route('/welcome', methods=['GET'])
def welcome():
    return jsonify({"status": 'Welcome to Anugrah Mobile apllication'})

@app.route('/auth', methods=['POST', 'GET'])
def auth():
    data = request.get_json()
    num = data.get('number')
    otp = generate_secure_otp(num)
    return jsonify({"otp": otp})

@app.route('/secure-chat', methods=['POST'])
def secure_chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input. Expected JSON data."}), 400

    sender_phone = data.get('sender_phone')
    receiver_phone = data.get('receiver_phone')
    message_content = data.get('message_content')
    # image_base64 = data.get('image_base64')
    image_base64 = False

    if not sender_phone or not receiver_phone or not message_content:
        return jsonify({"error": "All fields (sender_phone, receiver_phone, message_content) are required."}), 400

    file_path = None
    if image_base64:
        try:
            image_data = base64.b64decode(image_base64)
            image_format = imghdr.what(None, h=image_data)
            save_dir = os.path.join("data", "web3")
            file_name = f"{sender_phone}_{receiver_phone}.{image_format.lower()}" 
            file_path = os.path.join(save_dir, file_name)
            with open(file_path, "wb") as file:
                file.write(base64.b64decode(image_base64))
            
            print(f"Image saved to {file_path}")
        except Exception as e:
            return jsonify({"error": f"Invalid base64 image data. {e}"}), 400

    try:
        # Call a placeholder `send_message` function to handle the messaging logic
        send_message(int(sender_phone), int(receiver_phone), message_content, media_file_path=file_path)
        return jsonify({"process": 'done'})
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/get-user-msg', methods=['POST'])
def get_user_msg():
    phone = request.form.get('phone')
    if not phone:
        return jsonify({"error": "all the field are required."}), 400
    try:
        data = get_user_messages(int(phone))
        return jsonify({"user data": data})
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred.{e}"}), 500

@app.route('/text-translate', methods=['POST', 'GET'])
def translate():
    data = request.get_json()
    text = data.get('text')
    targetlang = data.get('targetlang')
    
    if not text or not targetlang:
        return jsonify({"error": "Both 'text' and 'targetlang' are required."}), 400
    
    translated_text = translate_text(text, targetlang)
    
    return jsonify({"translated_text": translated_text})

@app.route('/make-call', methods=['POST', 'GET'])
def make_call():
    data = request.get_json()
    number = data.get('number')
    
    if not number:
        return jsonify({"error": "number is required."}), 400

    try:
        sid = place_call(number)
        return jsonify(sid)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred. {str(e)}"}), 500

@app.route('/audio-to-text-base64', methods=['POST'])
def audiototext_with_base64():
    data = request.get_json()
    base64_audio = data.get('audio_base64')
    src = data.get('src')
    dest = data.get('dest')
    if not base64_audio:
        return jsonify({"error": "'audio_base64' field is required."}), 400
    try:
        recognized_text = base64_transcribe(base64_audio, src, dest, desc=True)
        return jsonify(recognized_text)
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/text-to-audio', methods=['POST', 'GET'])
def texttoaudio():
    data = request.get_json()
    text = data.get('text')
    src = data.get('src')
    dest = data.get('dest')
    voice = data.get('voice')
    
    if not text or not dest:
        return jsonify({"error": "Both 'text' and 'targetlang' are required."}), 400
    
    try:
        transliterate(text, dest, voice, True)
        return send_file(r"L:\ANUGRAGH BACKEND\backend\data\tts.mp3", as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred. {str(e)}"}), 500

@app.route('/text-to-sign', methods=['POST', 'GET'])
def texttosign(): 
    try:
        data = request.get_json()
        text = data.get('text')
        
        generate_isl_videos(text, save=True)
        
        # Read video file as base64
        base_path = r"L:\My projects\Anugrah\backend\data\text2sign\sign_video.mp4"
        with open(base_path, "rb") as video_file:
            video_base64 = base64.b64encode(video_file.read()).decode('utf-8')

        # Return the base64-encoded video
        return jsonify({"video_base64": video_base64})
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred. {str(e)}"}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        text = data.get('text')
        image = data.get('image')

        if not text and not image:
            return jsonify({"error": "Either 'text' or 'image' must be provided"}), 400

        conversation = session.get('conversation', [])

        if image:
            image_data = base64.b64decode(image)
            img = BytesIO(image_data)

            response = anugrah_Vision_Llama_v1(image=img, text_query=text, conversation=conversation)
        else:
            response = anugrah_Vision_Llama_v1(text_query=text, conversation=conversation)

        user_input = {"role": "user", "content": text or "[Image uploaded]"}
        assistant_response = {"role": "assistant", "content": response}
        conversation.extend([user_input, assistant_response])

        # Save
        session['conversation'] = conversation

        return jsonify({"response": response})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/video_sign', methods=['GET','POST'])
def video_sign():
    try:  
        video_file = request.files['video']
        src = request.form['src']
        dest = request.form['dest']
        base_path = 'data/video2'
        video_to_sign(video_file,  src, dest, base_path)
        
        base_path = r"L:\My projects\Anugrah\backend\data\video2\final_sign_video.mp4"
        
        with open(base_path, "rb") as video_file:
            video_base64 = base64.b64encode(video_file.read()).decode('utf-8')

        return jsonify({"video_base64": video_base64})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/youtube-video2-sign', methods=['POST', 'GET'])
def youtube_video2_sign():
    try:
        data = request.get_json()
        video_url = data.get('url')
        if not video_url:
            return jsonify({"error": "Video URL is required"}), 400
        src = data.get('src')
        dest = data.get('dest')

        youtube_vide_to_sign(video_url, src, dest)

        # Read video file as base64
        base_path = r"L:\My projects\Anugrah\backend\data\yt\final_sign_video.mp4"
        print('Video_Path:',base_path)
        with open(base_path, "rb") as video_file:
            video_base64 = base64.b64encode(video_file.read()).decode('utf-8')

        # Return the base64-encoded video
        return jsonify({"video_base64": video_base64})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/youtube-description', methods=['POST', 'GET'])
def youtube_description():
    try:
        data = request.get_json()
        video_url = data.get('url')
        if not video_url:
            return jsonify({"error": "Video URL is required"}), 400
        src = data.get('src')
        dest = data.get('dest')
        result = youtube_video_description(video_url, src, dest)
        return jsonify({"desc": result})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/youtube-summarize', methods=['POST', 'GET'])
def youtube_summarize():
    try:
        data = request.get_json()
        video_url = data.get('url')
        src = data.get('src')
        dest = data.get('dest')
        summary = youtube_video_description(video_url, src, dest, summarize=True)
        print(summary)
        return jsonify({"summary": summary})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/emotion', methods=['POST', 'GET'])
def youtube_emotion():
    try:
        data = request.get_json()
        text = data.get('text')
        response = emotion_det_text(text)
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/emotion-audio', methods=['POST', 'GET'])
def youtube_emotion_audio():
    try:
        data = request.get_json()
        text = data.get('text')
        audio_file_path = r'L:/My projects/Anugrah/backend/data/emo/output_audio.mp3'
        emotion_detect(text, audio_file_path)

        with open(audio_file_path, 'rb') as audio_file:
            encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

        return jsonify({"audio_base64": encoded_audio})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
