from aksharamukha import transliterate as trans
from deep_translator import GoogleTranslator
from pydub import AudioSegment
import numpy as np
import librosa
import torch
import soundfile as sf

from .code_mapping import code_map

device = 'cuda' if torch.cuda.is_available() else 'cpu' 

language = 'indic'
speaker = 'v3_indic'

model, example_text = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language=language,
    speaker=speaker,
)

model.to(device)
sample_rate = 48000

def translatetext(txt, dest, src):
    translated_text = GoogleTranslator(source=src, target=dest).translate(txt)
    return translated_text

def speed_down(audio, speed):  
    new_frame_rate = int(audio.frame_rate * speed)
    slower_sound = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
    return slower_sound

# def speed_up(audio, speed): 
#     y, sr = librosa.load(audio)
#     y_fast = librosa.effects.time_stretch(y, rate=speed)
#     return y_fast

def speed_up(audio,speed_factor):
    # audio = AudioSegment.from_file(input_file)
    # print(speed_factor)
    modified_audio = audio.speedup(playback_speed=speed_factor)
    # modified_audio.export(output_file, format="wav")
    return modified_audio

# speed_up(r'L:\SIH\Backend\out\audio.wav',0.75)
# def translatetext(txt, dest, src='english'):
#     s = str(code_mapping.get(src))
#     d = str(code_mapping.get(dest))
#     translated_text = GoogleTranslator(source=s, target=d).translate(txt)
#     return translated_text

def generate_silence(duration_ms):
    num_samples = int(44100 * duration_ms / 1000)
    silence_data = np.zeros(num_samples, dtype=np.int16)
    silence_audio_segment = AudioSegment(
        silence_data.tobytes(),
        frame_rate=44100,
        sample_width=silence_data.dtype.itemsize,
        channels=1
    )
    return silence_audio_segment

def transliterate(orig_text, language, gender, tts=False):
    gender_mapping = {
        'hindi': ('hindi_female', 'hindi_male'),
        'malayalam': ('malayalam_female', 'malayalam_male'),
        'manipuri': ('manipuri_female',),
        'bengali': ('bengali_female', 'bengali_male'),
        'rajasthani': ('rajasthani_female', 'rajasthani_male'),
        'tamil': ('tamil_female', 'tamil_male'),
        'telugu': ('telugu_female', 'telugu_male'),
        'gujarati': ('gujarati_female', 'gujarati_male'),
        'kannada': ('kannada_female', 'kannada_male'),
    }
    audio = AudioSegment.silent(duration=0)

    if language != 'tamil':
        language_mapping = {
            'hindi': 'Devanagari',
            'malayalam': 'Malayalam',
            'manipuri': 'Bengali',
            'bengali': 'Bengali',
            'rajasthani': 'Devanagari',
            'telugu': 'Telugu',
            'gujarati': 'Gujarati',
            'kannada': 'Kannada',
            'english':'English',
        }
        lang = language_mapping.get(language)
        print(language)
        print(lang)
        roman_text = trans.process(lang, 'ISO', orig_text)

        audio = model.apply_tts(roman_text,
                                speaker=gender_mapping.get(language)[0 if gender== 'female' else 1],
                                sample_rate=sample_rate)
        
        print(language_mapping.get(language), gender_mapping.get(language))
    else:
        roman_text = trans.process('Tamil', 'ISO', orig_text, pre_options=['TamilTranscribe'])

        audio = model.apply_tts(roman_text,
                                speaker=gender_mapping.get(language)[0 if gender== 'female' else 1],
                                sample_rate=sample_rate)
    print(1)
    if tts:
        audio_data = audio.numpy()
        scaled_audio_data = (audio_data * 32767).astype(np.int16)
        audio_segment = AudioSegment(scaled_audio_data.tobytes(), frame_rate=48000, sample_width=2, channels=1)
        audio_segment.export(r"L:\ANUGRAGH BACKEND\backend\data\tts.mp3", format="mp3")
        print(2)
    else:
        return audio

def text_to_speech(result, src, dest, gender):

    final_audio = AudioSegment.silent(duration=0)
    length = len(result)
    
    s = str(code_map(src))
    d = str(code_map(dest))
    
    # dest = code_mapping.get(dest)
    
    for i in range(length):
        if i < length-1:
            current_segment = result[i]
            next_segment = result[i + 1]
            
            difference = next_segment['start'] - current_segment['end']
            
            translated_txt = translatetext(current_segment['word'], d, s)

            audio_bytes = transliterate(translated_txt, dest, gender)

            audio_data = audio_bytes.numpy()
            scaled_audio_data = (audio_data * 32767).astype(np.int16)
            audio_segment = AudioSegment(scaled_audio_data.tobytes(), frame_rate=48000, sample_width=2, channels=1)
            print(type(audio_segment))

            # trans_duration = tensor_audio_segment.duration_seconds
            trans_duration = trans_duration = len(audio_segment) / 1000 
            og_duration = current_segment['end'] - current_segment['start']
            print(og_duration)
            print(trans_duration)

            ratio = og_duration / trans_duration
            print(ratio)

            # if ratio < 1:
            #     seg = speed_down(audio_segment, ratio)
            # else:
            #     seg = speed_up(audio_segment, ratio)
                
            # print(len(seg)/1000)
            # final_audio += seg
            final_audio += audio_segment

            if difference > 0:
                final_audio += generate_silence(difference * 1000)
            print(current_segment['word'])
            print(translated_txt)
        else:
            current_segment = result[i]
            
            translated_txt = translatetext(current_segment['word'], d, s)
            audio_bytes = transliterate(translated_txt, dest, gender)
            
            audio_data = audio_bytes.numpy()
            scaled_audio_data = (audio_data * 32767).astype(np.int16)
            audio_segment = AudioSegment(scaled_audio_data.tobytes(), frame_rate=48000, sample_width=2, channels=1)
            final_audio += audio_segment
            
            trans_duration = audio_segment.duration_seconds
            og_duration = current_segment['end'] - current_segment['start']

            ratio = og_duration / trans_duration

            # if ratio < 1:
            #     final_audio += speed_down(audio_segment, ratio)
            # else:
            #     final_audio += speed_up(audio_segment, ratio)
            final_audio += audio_segment
            print(current_segment['word'])
            print(translated_txt)

    final_audio.export("Female_audio_out.mp3", format="mp3")
