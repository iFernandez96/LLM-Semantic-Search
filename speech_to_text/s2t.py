import speech_recognition as sr
'''
pip install SpeechRecognition

bre install portaudio
pip install pyaudio

'''


def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now:")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    print("Converting...")
    try:
        value = r.recognize_google(audio)
        return value
    except sr.UnknownValueError:
        return "-1"
    except sr.RequestError:
        return "-2"


def main():
    result = speech_to_text()
    if result == "-1":
        print("Missed it")
    elif result == "-2":
        print("Processing error")
    else:
        print(result)

if __name__ == "__main__":
    main()
