import os
import time
from gtts import gTTS
import pyaudio
import wave

class TTSHandler:
    def __init__(self):
        self.AI_command = None
        self.AI_message = None

    def text_to_speech(self, text):
        # Generate a unique filename
        filename = "temp_"+ str(time.time())
        # Convert text to speech
        tts = gTTS(text=text, lang='en')
        tts.save(filename + ".mp3")

        # Convert mp3 file to wav because PyAudio works with wav files
        os.system(f'ffmpeg -y -i {filename}.mp3 {filename}.wav > NUL 2>&1')

        # Play the wav file
        chunk = 1024  
        f = wave.open(filename + ".wav","rb")  
        p = pyaudio.PyAudio()  
        stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                        channels = f.getnchannels(),  
                        rate = f.getframerate(),  
                        output = True)  
        data = f.readframes(chunk)  

        while data:  
            stream.write(data)  
            data = f.readframes(chunk)  

        stream.stop_stream()  
        stream.close()  
        p.terminate()
        f.close()

        # Remove the temporary files
        os.remove(filename + ".mp3")
        os.remove(filename + ".wav")


if __name__ == "__main__":
    tts_handler = TTSHandler()
    while True:
        time.sleep(1)
    