from moviepy.editor import VideoFileClip
from moviepy.editor import concatenate_videoclips
from moviepy.editor import CompositeVideoClip
from moviepy.editor import vfx
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from pydub import AudioSegment
from pytube import YouTube
import subprocess
import traceback
import whisper
import yt_dlp
import json
import nltk
import os

from .audiototext import audio2text

def mp3to_wav(mp3_path):
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export('wav_file.wav', format="wav")
        print("Conversion successful")
    except Exception as e:
        print(f"Error converting MP3 to WAV: {e}")

def generate_isl_videos(word, 
                        base_path="data/assets_sign", 
                        save=False):
    video_clips = []
    word_list = word_tokenize(word)

    tagged = nltk.pos_tag(word_list)
    tense = {
        "future": len([word for word in tagged if word[1] == "MD"]),
        "present": len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]]),
        "past": len([word for word in tagged if word[1] in ["VBD", "VBN"]]),
        "present_continuous": len([word for word in tagged if word[1] == "VBG"]),
    }
    stop_words = set([...])
    lr = WordNetLemmatizer()
    filtered_text = [
        lr.lemmatize(w, pos='v') if p[1] in ['VBG', 'VBD', 'VBZ', 'VBN', 'NN'] else 
        lr.lemmatize(w, pos='a') if p[1] in ['JJ', 'JJR', 'JJS', 'RBR', 'RBS'] else 
        lr.lemmatize(w)
        for w, p in zip(word_list, tagged) if w not in stop_words
    ]

    probable_tense = max(tense, key=tense.get)
    if probable_tense == "past" and tense["past"] >= 1:
        filtered_text.insert(0, "Before")
    elif probable_tense == "future" and tense["future"] >= 1:
        if "Will" not in filtered_text:
            filtered_text.insert(0, "Will")
    elif probable_tense == "present" and tense["present_continuous"] >= 1:
            filtered_text.insert(0, "Now") 
    
    for word in filtered_text:
        video_path = os.path.join(base_path, f"{word}.mp4")
        if not os.path.exists(video_path):
            for char in word:
                char_video_path = os.path.join(base_path, f"{char}.mp4")
                if os.path.exists(char_video_path):
                    video_clips.append(VideoFileClip(char_video_path))
        else:
            video_clips.append(VideoFileClip(video_path))

    if video_clips:
      final_clip = concatenate_videoclips(video_clips, method="compose")
      if save:
        output_path = os.path.join("data/text2sign", "sign_video.mp4")
        final_clip.write_videofile(output_path, codec="libx264", audio=False)
      return final_clip
    else:
      return None
    

def text_to_sign_youtube(results, 
                         main_video_path,
                         base_path, 
                         overlay_width=300, 
                         margin=10):
    try:
        video_clips = []
        main_video = VideoFileClip(main_video_path)
        for result in results:
            isl_video = generate_isl_videos(result.get('word'))
            if not isl_video:
                continue
            print(result.get('word'))
            
            isl_duration = isl_video.duration

            start_time = result.get('start', 0)
            end_time = result.get('end', isl_duration)
            org_dur = end_time - start_time

            if isl_duration > org_dur:
                speed_factor = isl_duration / org_dur
                isl_video = isl_video.fx(vfx.speedx, factor=speed_factor)

            video_clips.append((isl_video, start_time))
        print("process 1 done")
        # Overlay video
        clips = [main_video]
        for overlay_video, start_time in video_clips:
            overlay_video = overlay_video.resize(width=overlay_width)
            overlay_position = (main_video.size[0] - overlay_video.size[0] - margin, 
                                main_video.size[1] - overlay_video.size[1] - margin)
            overlay_video = overlay_video.set_position(overlay_position).set_start(start_time).set_duration(
                main_video.duration - start_time
            )
            clips.append(overlay_video)
        final_video = CompositeVideoClip(clips)
        print("process 2 done")
        out_path = base_path+"/final_sign_video.mp4"
        final_video.write_videofile(out_path, codec="libx264", audio_codec="aac")

        print(f"Final video with ISL overlay generated at: {out_path}")

    except Exception as e:
        print(f"Error in text_to_sign_youtube: {str(e)}")
        traceback.print_exc()

    finally:
      if 'isl_video' in locals() and isl_video is not None:
          isl_video.close()
      if 'main_video' in locals():
          main_video.close()


def youtube_vide_to_sign(video_url, src, dest):
    # Download video and audio
    yt = YouTube(video_url)
    base_path = "data/yt"
    os.makedirs(base_path, exist_ok=True)
        
    try:
        with yt_dlp.YoutubeDL({
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'data/yt/video.%(ext)s',
        }) as ydl:
            ydl.download([video_url])
        print("Video with audio download complete!")

        with yt_dlp.YoutubeDL({
            'format': 'bestaudio/best',
            'outtmpl': 'data/yt/audio.%(ext)s',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }
            ],
        }) as ydl:
            ydl.download([video_url])
        print("Audio extraction (WAV format) complete!")
    except Exception as e:
        print(f"An error occurred during download: {e}")

    #processing
    result = audio2text('data/yt/audio.wav', src, dest, base_path)
    text_to_sign_youtube(result, 'data/yt/video.webm', base_path)


# youtube_vide_to_sign('https://www.youtube.com/shorts/XcS7ih3bZzo', 'english', 'hindi')

# result = [
#   {
#     "start": 0.0,
#     "end": 3.3200000000000003,
#     "word": " Here's your quick tutorial on how to sound more American.",
#     "tword": "\u092f\u0939\u093e\u0902 \u092a\u0930 \u0906\u092a\u0915\u094b \u0905\u0927\u093f\u0915 \u0905\u092e\u0947\u0930\u093f\u0915\u0940 \u0932\u0917\u0928\u0947 \u0915\u093e \u0924\u094d\u0935\u0930\u093f\u0924 \u091f\u094d\u092f\u0942\u091f\u094b\u0930\u093f\u092f\u0932 \u0926\u093f\u092f\u093e \u0917\u092f\u093e \u0939\u0948\u0964"
#   },
#   {
#     "start": 3.3200000000000003,
#     "end": 7.84,
#     "word": " So Marina arrived in the US in 2015 and she sounded like this.",
#     "tword": "\u0924\u094b \u092e\u0930\u0940\u0928\u093e 2015 \u092e\u0947\u0902 \u0905\u092e\u0947\u0930\u093f\u0915\u093e \u092a\u0939\u0941\u0902\u091a\u0940 \u0914\u0930 \u0909\u0938\u0915\u0940 \u0906\u0935\u093e\u091c\u093c \u0915\u0941\u091b \u0910\u0938\u0940 \u0925\u0940\u0964"
#   },
#   {
#     "start": 7.84,
#     "end": 9.200000000000001,
#     "word": " What are you doing?",
#     "tword": "\u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930 \u0930\u0939\u0947 \u0939\u094b?"
#   },
#   # {
#   #   "start": 9.200000000000001,
#   #   "end": 10.92,
#   #   "word": " Because I learned British English at school.",
#   #   "tword": "\u0915\u094d\u092f\u094b\u0902\u0915\u093f \u092e\u0948\u0902\u0928\u0947 \u0938\u094d\u0915\u0942\u0932 \u092e\u0947\u0902 \u092c\u094d\u0930\u093f\u091f\u093f\u0936 \u0905\u0902\u0917\u094d\u0930\u0947\u091c\u0940 \u0938\u0940\u0916\u0940 \u0925\u0940\u0964"
#   # },
#   # {
#   #   "start": 10.92,
#   #   "end": 12.68,
#   #   "word": " And my American friend told me,",
#   #   "tword": "\u0914\u0930 \u092e\u0947\u0930\u0947 \u0905\u092e\u0947\u0930\u093f\u0915\u0940 \u092e\u093f\u0924\u094d\u0930 \u0928\u0947 \u092e\u0941\u091d\u0938\u0947 \u0915\u0939\u093e,"
#   # },
#   # {
#   #   "start": 12.68,
#   #   "end": 14.76,
#   #   "word": " No, no, no, Marina, not like that.",
#   #   "tword": "\u0928\u0939\u0940\u0902, \u0928\u0939\u0940\u0902, \u0928\u0939\u0940\u0902, \u092e\u0930\u0940\u0928\u093e, \u0910\u0938\u093e \u0928\u0939\u0940\u0902 \u0939\u0948\u0964"
#   # },
#   # {
#   #   "start": 14.76,
#   #   "end": 16.88,
#   #   "word": " If you want to sound more American, you say,",
#   #   "tword": "\u092f\u0926\u093f \u0906\u092a \u0905\u0927\u093f\u0915 \u0905\u092e\u0947\u0930\u093f\u0915\u0940 \u0932\u0917\u0928\u093e \u091a\u093e\u0939\u0924\u0947 \u0939\u0948\u0902, \u0924\u094b \u0906\u092a \u0915\u0939\u0947\u0902\u0917\u0947,"
#   # },
#   # {
#   #   "start": 16.88,
#   #   "end": 18.52,
#   #   "word": " What are you doing?",
#   #   "tword": "\u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930 \u0930\u0939\u0947 \u0939\u094b?"
#   # },
#   # {
#   #   "start": 18.52,
#   #   "end": 19.8,
#   #   "word": " What are you doing?",
#   #   "tword": "\u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930 \u0930\u0939\u0947 \u0939\u094b?"
#   # },
#   # {
#   #   "start": 19.8,
#   #   "end": 21.0,
#   #   "word": " What are you up to?",
#   #   "tword": "\u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930 \u0930\u0939\u0947 \u0939\u0948\u0902?"
#   # },
#   # {
#   #   "start": 21.0,
#   #   "end": 22.12,
#   #   "word": " What is going on?",
#   #   "tword": "\u0915\u094d\u092f\u093e \u0939\u094b \u0930\u0939\u093e \u0939\u0948?"
#   # },
#   # {
#   #   "start": 22.12,
#   #   "end": 23.240000000000002,
#   #   "word": " What are you doing?",
#   #   "tword": "\u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930 \u0930\u0939\u0947 \u0939\u094b?"
#   # },
#   # {
#   #   "start": 23.240000000000002,
#   #   "end": 24.16,
#   #   "word": " What are you up to?",
#   #   "tword": "\u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930 \u0930\u0939\u0947 \u0939\u0948\u0902?"
#   # },
#   # {
#   #   "start": 24.16,
#   #   "end": 25.080000000000002,
#   #   "word": " Subscribe for more.",
#   #   "tword": "\u0905\u0927\u093f\u0915 \u091c\u093e\u0928\u0915\u093e\u0930\u0940 \u0915\u0947 \u0932\u093f\u090f \u0938\u0926\u0938\u094d\u092f\u0924\u093e \u0932\u0947\u0902."
#   # }
# ]

# # text_to_sign_youtube(result, r'L:\ANUGRAGH BACKEND\backend\data\yt\video.webm')


# # generate_isl_videos('What are you doing?')