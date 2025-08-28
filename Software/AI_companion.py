import speech_recognition as sr
import google.generativeai as genai
import requests
import time
import uuid
import os
import pygame
import threading
from cvzone.SerialModule import SerialObject
from time import sleep
from playsound import playsound
from dotenv import load_dotenv

#---------------------Initialization------------------------------

#---------------------Servo Movements--------------------

# Create a Serial object with three digits precision for sending servo angles
arduino = SerialObject("/dev/tty.usbmodem101", digits=3)

# Initialize the last known positions for the three servos: Left (LServo), Right (RServo), Head (HServo)
# LServo starts at 180 degrees, RServo at 0 degrees, and HServo at 90 degrees
last_positions = [0, 0, 90]


#---------------------Initialize Gemini API--------------------------
load_dotenv()
API_KEY = os.getenv("Gemini_api_key")
genai.configure(api_key="API_KEY")


#---------------------Camb.ai TTS function---------------------------
load_dotenv()
API_KEY2 = os.getenv("Camb_api_key")
def text_to_speech_camb(text, voice_id=20305, language=1, gender=1, age=30, api_key="API_KEY2"):
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "voice_id": voice_id,
        "language": language,
        "gender": gender,
        "age": age
    }

    # Submit request
    response = requests.post("https://client.camb.ai/apis/tts", headers=headers, json=payload)
    response.raise_for_status()
    task_id = response.json()["task_id"]
    print(f"Task submitted! Task ID: {task_id}")

    # Poll for completion
    while True:
        status_response = requests.get(f"https://client.camb.ai/apis/tts/{task_id}", headers=headers)
        status_data = status_response.json()
        if status_data["status"] == "SUCCESS":
            run_id = status_data["run_id"]
            break
        elif status_data["status"] == "FAILED":
            raise Exception("Speech generation failed.")
        print("Waiting for audio...")
        time.sleep(2)

    # Download audio
    audio_response = requests.get(f"https://client.camb.ai/apis/tts-result/{run_id}", headers=headers, stream=True)
    filename = f"{uuid.uuid4()}.wav"
    with open(filename, "wb") as f:
        for chunk in audio_response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    print(f"Audio saved as {filename}")
    playsound(filename)
    os.remove(filename)

# Gemini response function
def generate_response(text):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
    response = model.generate_content(text)
    print("Gemini says:", response.text)
    return response.text

#----------------------Keyword-based audio mapping----------------------
keyword_audio_map = {
    "ipl trophy:":"../Resources/rcb.mp3.mp3",
    "virat": "../Resources/virat.wav"
}

pygame.mixer.init()
#function to play prompt audios
def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(5)

#----------------------------Speech-to-text------------------------
def listen_with_google():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Your AI companion is listening...")
        play_sound("../Resources/listen.mp3")
        audio = recognizer.listen(source)
        play_sound("../Resources/convert.mp3")
        try:
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand.")
            return ""
        except sr.RequestError as e:
            print("Could not request results; check internet.")
            return ""


# -------------------Movement Functions -------------------

# Function to smoothly move servos to target positions
def move_servo(target_positions, delay=0.0001):
    """
    Moves the servos smoothly to the target positions.

    :param target_positions: List of target angles [LServo, RServo, HServo]
    :param delay: Time delay (in seconds) between each incremental step
    """
    global last_positions  # Use the global variable to track servo positions
    # Calculate the maximum number of steps required for the largest position difference
    max_steps = max(abs(target_positions[i] - last_positions[i]) for i in range(3))

    # Incrementally move each servo to its target position over multiple steps
    for step in range(max_steps):
        # Calculate the current position of each servo at this step
        current_positions = [
            last_positions[i] + (step + 1) * (target_positions[i] - last_positions[i]) // max_steps
            if abs(target_positions[i] - last_positions[i]) > step else last_positions[i]
            for i in range(3)
        ]
        # Send the calculated positions to the Arduino
        arduino.sendData(current_positions)
        # Introduce a small delay to ensure smooth motion
        sleep(delay)

    # Update the last known positions to the target positions
    last_positions = target_positions[:]


# ------------------------Hello gesture--------------------------

def hello_gesture():
  """
  Makes Robot wave hello by moving the right servo back and forth.
  """
  global last_positions
  # Move right arm to start waving
  move_servo([last_positions[0], 120, last_positions[2]])
  for _ in range(3):  # Perform the waving motion 3 times
     move_servo([last_positions[0], 150, last_positions[2]])  # Move arm slightly down
     move_servo([last_positions[0], 110, last_positions[2]])  # Move arm back up
  # Reset arm to original position
  move_servo([last_positions[0], 0, last_positions[2]])

# -------------------------Answer gesture-------------------------

def answer_gesture():
    """
    Makes Robot wave hand and head while answering.
    """
    global last_positions
    # Move right arm to start wave
    move_servo([last_positions[0],120,last_positions[2]])
    sleep(0.3)

    for _ in range(4):
        move_servo([last_positions[0], 150, last_positions[2]])  # Move right arm slightly down
        sleep(0.2)
        move_servo([last_positions[0], 110, last_positions[2]])  # Move right arm back up
        sleep(0.2)
        move_servo([last_positions[0], 150, 70])
        move_servo([last_positions[0], 110, 90])
     # Reset arm to original position
    move_servo([last_positions[0], 0, last_positions[2]])

#--------------------------shy gesture------------------------------

def dance_gesture():
    """
    A cute, shy gesture where the robot tilts its head and raises both arms.
    """
    global last_positions

    # Step 1: Tilt head slightly right
    move_servo([0, 0, 70], delay=0.005)  # Tilt head to 70 degrees

    # Step 2: Raise both arms slowly
    move_servo([120, 130, 80], delay=0.005)  # L arm up, R arm partially up

    # Step 3: Pause and 'hold the blush'
    sleep(1.5)

    # Step 4: Wiggle slightly like embarrassed
    move_servo([120, 120, 90], delay=0.005)
    move_servo([110, 110, 70], delay=0.005)
    move_servo([120, 120, 80], delay=0.005)
    move_servo([110, 110, 90], delay=0.005)
    # Step 5: Reset back to idle position
    move_servo([0, 0, 90], delay=0.005)


#----------------------Main Loop-----------------------
while True:

    # Movement for casual gesture
    move_servo([0, 0, 90], delay=0.005)

    # Listen for Speech input
    text = listen_with_google()

    # Wave hand if "Hello" or "Hi"
    if "hello" in text.lower() or "hi" in text.lower() or "Atria" in text.lower() or "how are you" in text.lower():
        print("Triggering Hello Gesture...")
        hello_gesture()

        response_text = "Hello! Good morning! How can i assist you today?"
        text_to_speech_camb(response_text)
        continue

    if "dance" in text.lower() or "can you dance" in text.lower() or "can u dance for me " in text.lower():
        text_to_speech_camb("Sure why not?")
        dance_gesture()
        dance_gesture()
        dance_gesture()
        text_to_speech_camb("Aww, thank you ! your making me shy!")
        continue

    if "who won the ipl trophy recently" in text.lower() or "trophy" in text.lower() or "who won" in text.lower():
        answer_gesture()
        text_to_speech_camb("Finally after eighteen years of long wait we won....Jai RCB esala cup namdu")
        answer_gesture()
        continue

    if "can u tell me about yourself" in text.lower() or "yourself" in text.lower() or "introduce yourself" in text.lower():
        answer_gesture()
        text_to_speech_camb("sure...for the time being i dont have a name...but i'm sure soon rahul and his team gonna find a name for me...and to tell about myself..I'm not just a average robot. I’m a smart, voice-powered AI assistant designed by Rahul and his team.I can move, talk, and even interact with my surroundings. Whether it’s answering questions, or helping out with everyday tasks, and more than that i'm your smart friend")
        answer_gesture()
        continue

    if "can u tell me about today weather" in text.lower() or "weather" in text.lower() or "weather in bangalore" in text.lower():
        answer_gesture()
        text_to_speech_camb("sure...Today's minimum temperature in Bangalore is recorded at twenty one degrees celsius, and the maximum temperature is expected to go as high as thirty degrees celsius. ")
        answer_gesture()
        continue

    if "can you tell me the components used in you" in text.lower() or "components used" in text.lower():
        text_to_speech_camb("sure")
        answer_gesture()
        text_to_speech_camb("I have been built using a variety of powerful hardware and software components.On the hardware side, I run on servo motors, an Arduino Uno, a sensor shield, and many more electronic parts working together in harmony.And when it comes to software, I’m powered by Google’s Gemini AI and Rahul’s intelligent system — a smart combo that brings me to life!")
        answer_gesture()
        continue

    if "can you tell me a joke" in text.lower() or "tell a joke" in text.lower() or "joke" in text.lower():
        text_to_speech_camb("sure")
        answer_gesture()
        text_to_speech_camb("why did the robot go to school...to improve its syntax...ha ha ha ha ha...did you like it")
        continue

    if "planning to join atria institute of technology get me some suggestions" in text.lower() or "tell about atria institute of technology" in text.lower() or "get me some suggestions" in text.lower() or "tell me about atria institute of technology" in text.lower():
        answer_gesture()
        text_to_speech_camb("Absolutely! Atria Institute of Technology is an exciting place to learn, grow, and build your future. Whether you're into AI, robotics, data science, or coding,or it can be any field there’s a lot here for you! The campus is friendly and buzzing with tech events, student clubs, and real-world projects.We’ve got great faculty, well-equipped labs, and tons of opportunities to explore your passion. From hackathons to innovation fests — it’s not just a college, it’s a creative playground.")
        answer_gesture()
        continue

    if "can your wave your hand" in text.lower() or "can u move your hand" in text.lower():
        hello_gesture()
        continue
    else:
        # Otherwise, continue with AI response
        ai_response = generate_response(text)
        answer_gesture()
        text_to_speech_camb(ai_response, voice_id=20305, language=1, gender=1, age=25, api_key="API_KEY2")
        answer_gesture()
        continue




