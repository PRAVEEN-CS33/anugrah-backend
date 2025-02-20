from transformers import pipeline
import torch
import yt_dlp
from pytube import YouTube
import os

from .audiototext import audio2text

def summarize_text(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text['recognized_text'], do_sample=False)
    summary = summary[0]['summary_text']
    return summary

def youtube_video_description(video_url, src, dest, summarize=False):
    yt = YouTube(video_url)
    base_path = "data/desc"
    try:
        with yt_dlp.YoutubeDL({
            'format': 'bestaudio/best',
            'outtmpl': 'data/desc/audio.%(ext)s',
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

    result = audio2text('data/desc/audio.wav', src, dest, base_path, desc=True)
    
    if summarize:
        return summarize_text(result)
    
    return result
