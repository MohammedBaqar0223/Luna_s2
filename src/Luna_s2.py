import requests
import speech_recognition as sr
import pyttsx3
import openai
import os
from dotenv import load_dotenv
from sympy import false,true
import json

load_dotenv()

r = sr.Recognizer()
engine = pyttsx3.init()
ollama = openai.OpenAI(base_url="http://localhost:11434/v1", api_key=os.getenv("OLLAMA_API_KEY"))
result = ""
check = false
weath_api_key ="e6be0f7f9b53eab93315137b14f1f6c0"
NASA_HIT = ["nasa","nasa facts","space facts","astronomy facts","space","astronomy"]
NAME_HIT = ["what is your name","who are you"]
NASA_ASTRO_HIT = ["nearest asteroid","near asteroid","asteroid","nearby asteriod"]
WEATHER_HIT=["weather","current weather"]

def say(text):
    voices = engine.getProperty('voices')
    engine.setProperty('voice',voices[1].id)
    engine.say(text)
    engine.runAndWait()

def get_audio():
    with sr.Microphone(device_index=1) as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source,duration=1)
        audio = r.listen(source)

        print("Audio captured!")
        print(audio)
        print("Thinking....")

        try :
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            unknown = "Sorry, I did not understand that."
            print(unknown)
            say(unknown)
            return None
        except sr.RequestError as e:
            error = f"Error fetching results from Google Speech Recognition service; {e}"
            print(error)
            say(error)
            return None

while true:
    text = get_audio()
    if text is None:
        continue
    for phrase in NASA_HIT:
        if phrase in text.lower():
            for attempt in range(3):
                response = requests.get(
                    "https://api.nasa.gov/planetary/apod",
                    params = {"api_key": os.getenv("NASA_API_KEY"), "count" : 1}
                )
                if response.status_code == 200: ## getting random space / astronomy fact and image from apod
                    data = response.json()[0]
                    image_url = data.get("hdurl") or data.get("url")
                    image_get = requests.get(image_url).content
                    with open("apod_image.jpg", "wb") as f:
                        f.write(image_get)
                    os.startfile("apod_image.jpg")
                    say(data.get("explanation"))
                    print("Title:", data.get("title"))
                    print("Image_URL:", data.get("url"))
                    print("Explanation:", data.get("explanation"))                       
                    print("Image saved as apod_image.jpg")
                    check = true
                    break
    
    for phrase in NAME_HIT:
        if phrase in text.lower():
            result = "I am luna your personal assistant, how can I help you today?"
            say(result)
            check = true
    
    for phrase in NASA_ASTRO_HIT:
        if phrase in text.lower():
            response = requests.get(
                "https://api.nasa.gov/neo/rest/v1/feed",
                params = {"api_key": os.getenv("NASA_API_KEY"), "start_date" : "2024-06-01", "end_date" : "2024-06-07"}
            )
            if response.status_code == 200: ## getting nearest asteroid data from nasa api
                data = response.json()
                near_asteroid = data.get("near_earth_objects")
                for date in near_asteroid:
                    for asteroid in near_asteroid[date]:
                        name = asteroid.get("name")
                        diameter = asteroid.get("estimated_diameter").get("meters").get("estimated_diameter_max")
                        velocity = asteroid.get("close_approach_data")[0].get("relative_velocity").get("kilometers_per_hour")
                        distance = asteroid.get("close_approach_data")[0].get("miss_distance").get("kilometers")
                        result = f"The nearest asteroid is {name} with a diameter of {diameter} meters, traveling at a velocity of {velocity} km/h and is {distance} km away from Earth."
                        say(result)
                        print(result)
                        check = true
        break

    for phrases in WEATHER_HIT:
        if phrases in text.lower():
            response=requests.get(
                "http://api.weatherstack.com/current",
                params={
                    "access_key":weath_api_key,
                    "query":"Bangalore"
                }
            )
            data = response.json()
            say(data["current"]["weather_descriptions"][0])
            print(data["current"]["weather_descriptions"[0]])
            check = true

    if check == false: ## generating ai responses
        response = ollama.chat.completions.create(
        model = "llama3.2:latest",
        messages = [
            {"role": "system", "content": "You are a helpful assistant that responds to user queries."},
            {"role": "user", "content": text}
        ]
    )
        result = response.choices[0].message.content
    print(f"Response: {result}")
    say(result)
    check = false