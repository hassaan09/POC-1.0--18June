import json
import speech_recognition as sr
from pydub import AudioSegment
from typing import Optional, Union
import os

class InputProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def process_input(self, text_input: Optional[str] = None, 
                     audio_file: Optional[str] = None, 
                     transcript_file: Optional[str] = None) -> str:
        """
        Process different input types and return normalized text
        """
        if text_input and text_input.strip():
            return text_input.strip()
        
        if audio_file:
            return self._transcribe_audio(audio_file)
        
        if transcript_file:
            return self._read_transcript_file(transcript_file)
        
        return ""
    
    def _transcribe_audio(self, audio_file: str) -> str:
        """
        Transcribe audio file to text
        """
        try:
            # Convert audio to WAV if needed
            if not audio_file.lower().endswith('.wav'):
                audio = AudioSegment.from_file(audio_file)
                wav_file = audio_file.rsplit('.', 1)[0] + '.wav'
                audio.export(wav_file, format="wav")
                audio_file = wav_file
            
            # Transcribe using speech recognition
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        
        except Exception as e:
            print(f"Audio transcription error: {e}")
            return ""
    
    def _read_transcript_file(self, file_path: str) -> str:
        """
        Read transcript from file (supports .txt and .json)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.lower().endswith('.json'):
                    data = json.load(f)
                    # Handle different JSON formats
                    if isinstance(data, dict):
                        return data.get('text', '') or data.get('transcript', '') or str(data)
                    elif isinstance(data, list):
                        return ' '.join([str(item) for item in data])
                    else:
                        return str(data)
                else:
                    return f.read()
        
        except Exception as e:
            print(f"File reading error: {e}")
            return ""