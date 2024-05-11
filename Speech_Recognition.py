import speech_recognition as sr
import requests
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import RPi.GPIO as GPIO
import time

# GPIO setup
RED_LED = 17  # Change to your GPIO pin
BLUE_LED = 27  # Change to your GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BLUE_LED, GPIO.OUT)

# Initialize the recognizer
r = sr.Recognizer()

# Function to play an audio file from a URL
def play_audio_from_url(url):
    response = requests.get(url)
    audio_segment = AudioSegment.from_file(BytesIO(response.content), format="m4a")
    play(audio_segment)

def control_lights(command):
    if "turn red light on" in command:
        GPIO.output(RED_LED, GPIO.HIGH)
    elif "turn red light off" in command:
        GPIO.output(RED_LED, GPIO.LOW)
    elif "turn blue light on" in command:
        GPIO.output(BLUE_LED, GPIO.HIGH)
    elif "turn blue light off" in command:
        GPIO.output(BLUE_LED, GPIO.LOW)
    elif "turn red and blue light on" in command or "turn blue and red light on" in command:
        GPIO.output(RED_LED, GPIO.HIGH)
        GPIO.output(BLUE_LED, GPIO.HIGH)
    elif "turn red and blue light off" in command or "turn blue and red light off" in command:
        GPIO.output(RED_LED, GPIO.LOW)
        GPIO.output(BLUE_LED, GPIO.LOW)

# Function to continuously listen and recognize speech
def recognize_speech():
    failed_attempts = 0
    active = False
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("System ready. Say 'Hey Jarvis' to activate.")
        while True:
            try:
                audio = r.listen(source, timeout=1, phrase_time_limit=5)
                text = r.recognize_google(audio).lower()
                print("Recognized: " + text)

                if "hey jarvis" in text and not active:
                    active = True
                    failed_attempts = 0
                    play_audio_from_url('https://github.com/Kenneth0120/Task7.2DAudioProcessing/blob/main/Voice/Hi_I_am_Jarvis.m4a?raw=true')
                    print("Hi, I am Jarvis. What can I help you?")

                elif active:
                    if any(cmd in text for cmd in ["turn red light on", "turn red light off", "turn blue light on", "turn blue light off", "turn red and blue light on", "turn red and blue light off", "turn blue and red light on", "turn blue and red light off"]):
                        control_lights(text)
                        failed_attempts = 0  # Reset on successful command
                        play_audio_from_url('https://github.com/Kenneth0120/Task7.2DAudioProcessing/blob/main/Voice/Ok_no_problem.m4a?raw=true')
                        print("Command executed: " + text)
                        print("Ok, no problem")
                    else:
                        print("Command not recognized. Please try again.")
                        failed_attempts += 1
                        if failed_attempts >= 10:
                            active = False
                            print("Deactivating after 10 failed commands. Say 'Hey Jarvis' to reactivate.")
            except sr.UnknownValueError:
                print("Could not understand audio, try again.")
                if active:
                    failed_attempts += 1
                    if failed_attempts >= 10:
                        active = False
                        print("Deactivating after 10 failed commands. Say 'Hey Jarvis' to reactivate.")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            except sr.WaitTimeoutError:
                print("No speech detected, try speaking again.")

# Call the function to start recognizing speech
recognize_speech()
