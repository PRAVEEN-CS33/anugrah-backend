# import vosk
# import json
# import wave

# model = vosk.Model("vosk-model-en-us-0.42-gigaspeech")

# def speech_to_text_from_file(audio_file_path):
#     try:
#         with wave.open(audio_file_path, "rb") as wf:
#             if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
#                 raise ValueError("Audio file must be mono, 16-bit PCM, and 16kHz sample rate.")

#             rec = vosk.KaldiRecognizer(model, wf.getframerate())

#             recognized_text = ""

#             while True:
#                 data = wf.readframes(4000)
#                 if len(data) == 0:
#                     break
#                 if rec.AcceptWaveform(data):
#                     result = json.loads(rec.Result())
#                     recognized_text += result.get('text', '') + " "

#             final_result = json.loads(rec.FinalResult())
#             recognized_text += final_result.get('text', '')

#             return recognized_text.strip()

#     except Exception as e:
#         print(f"Error processing audio file: {e}")
#         return ""

# audio_path = r"L:\ANUGRAGH BACKEND\backend\data\input\InputTamil.wav"
# recognized_text = speech_to_text_from_file(audio_path)
# print("Recognized Text:", recognized_text)



import subprocess
import wave
import vosk
import json

model_path = "models\vosk-model-small-hi-0.22"
output_file_path = "recognized_text.txt"

def convert_audio_to_wav(input_audio_path, output_audio_path):
    command = [
        "ffmpeg", "-i", input_audio_path,
        "-ar", "16000", "-ac", "1", "-sample_fmt", "s16",
        output_audio_path
    ]
    subprocess.run(command, check=True)

def speech_to_text_from_file(audio_file_path):
    try:
        converted_audio_path = "converted_audio.wav"
        convert_audio_to_wav(audio_file_path, converted_audio_path)

        print("Loading model...")
        model = vosk.Model(model_path)

        wf = wave.open(converted_audio_path, "rb")
        rec = vosk.KaldiRecognizer(model, wf.getframerate())

        with open(output_file_path, "w") as output_file:
            print("Processing audio file...")
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    recognized_text = result.get("text", "")
                    output_file.write(recognized_text + "\n")
                    print(recognized_text)

            final_result = json.loads(rec.FinalResult())
            final_text = final_result.get("text", "")
            output_file.write(final_text + "\n")
            print(final_text)

        wf.close()
        print(f"Recognized text saved to: {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
speech_to_text_from_file("data\input\InputHindi.wav")


