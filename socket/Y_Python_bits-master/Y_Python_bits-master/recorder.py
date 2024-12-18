import pyaudio
import speech_recognition as sr
import playsound

r = sr.Recognizer()
audio = None
f = None


def record_sound():
    global audio
    with sr.Microphone() as source:
        print("Say something!")
        r.adjust_for_ambient_noise(source)
        # background noise reduction (not very accurate)
        audio = r.listen(source)
        # Creating audio file required
        return


def save_sound():
    global audio, f
    f = open(f'audio_file1.wav', 'wb')
    # saving file
    f.write(audio.get_wav_data())
    #  getting wav data from recoreded audio
    f.close()


def play_sound():
    global f
    playsound.playsound('audio_file1.wav')
    # using playsound module to play the saved audio


record_sound()
save_sound()
play_sound()
