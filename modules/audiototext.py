import whisper
import librosa
import torch
import json
import os
from deep_translator import GoogleTranslator

from .code_mapping import code_map
from .emotiondet import emotion_det_text

LANG = {
    "english": "en",
    "hindi": "hi",
    "tamil": "ta",
    "telugu": "te",
    "bengali": "bn",
    "gujarati": "gu",
    "marathi": "mr",
    "kannada": "kn",
    "malayalam": "ml",
    "punjabi": "pa",
}

model = whisper.load_model("small")

def trans_text(text, target_lang="english"):
    target_lang = code_map(target_lang)
    translated_text = GoogleTranslator(source="auto", target=target_lang).translate(text)
    return translated_text

def audio2text(path, src, dest, base_path, local=False, desc=False):
    src = LANG.get(src)
    audio, sr = librosa.load(path, sr=16000)
    print(src,dest)
    result = model.transcribe(audio, language=src, fp16=False, verbose=True)
    print(result['text'])
    
    if desc:
        tword = trans_text(result["text"], dest)
        emotion = emotion_det_text(result["text"])
        responce = {
            'recognized_text':result["text"],
            'tword': tword,
            "type": "text",
            "emotion": emotion.get('emotion'),
            "emoji": emotion.get('emoji')
        }
        return responce
    
    result_data = []
    for i, seg in enumerate(result['segments']):
        tw = trans_text(seg['text'], dest)
        entry = {
            'start': seg['start'],
            'end': seg['end'],
            'word': seg['text'],
            'tword':tw,
        }
        result_data.append(entry)
    json_path = os.path.join(base_path, "result.json")
    with open(json_path, 'w') as json_file:
        json.dump(result_data, json_file, indent=2)
          
    return result_data

# print(audio2text(r'L:\My projects\Anugrah\backend\data\input\InputTamil.wav',
#            'tamil',
#            'english',
#            'data\outputs',
#            desc=True))

# import assemblyai as aai
# aai.settings.api_key = "31567524f31f41f3b75f25c3e6e9717e"
# transcriber = aai.Transcriber()
