import base64
import moviepy.editor as mp
import tempfile
import os
import numpy as np

from .audiototext import audio2text
from .generate_isl import text_to_sign_youtube

def videotoaudio(video_file, base_path):
    with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
        temp_video_file.write(video_file.read())
        temp_video_file_path = temp_video_file.name

    video_clip = mp.VideoFileClip(temp_video_file_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(base_path+"/audio.wav", codec='pcm_s16le', ffmpeg_params=["-ac", "2"])

    clip = video_clip.set_audio(None)
    clip.write_videofile(base_path+"/video.mp4", codec="libx264", audio_codec="aac")
    video_clip.close()
    os.remove(temp_video_file_path)
    
def video_to_sign(video_file, src, dest, base_path):
    videotoaudio(video_file, base_path)
    audio_path = os.path.join(base_path, "audio.wav")
    result = audio2text(audio_path, src, dest, base_path)
    text_to_sign_youtube(result, 'data/video2/video.mp4', base_path)
    return None