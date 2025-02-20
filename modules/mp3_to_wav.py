from pydub import AudioSegment

def mp3to_wav(mp3_path):
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export('wav_file.wav', format="wav")
        print("Conversion successful")
    except Exception as e:
        print(f"Error converting MP3 to WAV: {e}")