import azure.cognitiveservices.speech as speechsdk
import openai
import json
import requests
import subprocess
import urllib.parse
import time
import os
import io
import google.generativeai as genai
from opener import SmartAndroidAssistant
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

GEMINI_API_KEY = "AIzaSyDPwijZg1zvbofMjpdVogd3yABXcwP7Otc"  # Replace with your API key
genai.configure(api_key=GEMINI_API_KEY)

# 🔹 Azure Credentials
SPEECH_KEY = "3nF1650hHykjRygiBdmSgJQ8U08bOXEmgGXz8qIFlbya8Wa3UUDzJQQJ99BBACYeBjFXJ3w3AAAYACOGIx0Z"
SPEECH_REGION = "eastus"

AZURE_ENDPOINT = "https://horizon-test1711.cognitiveservices.azure.com/"
AZURE_KEY = "6a2U9CnbPO2JqPY9Doi5LEVemTW0F5jI6nVnFg0Td1JGCvGCi2l0JQQJ99BBACYeBjFXJ3w3AAAFACOGC0BT"

FLASK_API_URL = "http://127.0.0.1:5000/start-navigation"

openai.api_type = "azure"
openai.api_key = "2vYQo6xlAVhogi0UI8VeFGAQUylxg1ZUFQPBMlC3wCrLs9Suzf4SJQQJ99BBACfhMk5XJ3w3AAAAACOGjuFF"
openai.api_base = "https://20231-m6xs5g85-swedencentral.openai.azure.com/"
openai.api_version = "2023-06-01-preview"

# Initialize the Computer Vision Client
cv_client = ComputerVisionClient(AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_KEY))

# 🎤 Recognize Speech
def recognize_speech():
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("🎤 Speak now...")
    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"📝 Recognized Text: {result.text}")
        return result.text
    elif result.reason in [speechsdk.ResultReason.NoMatch, speechsdk.ResultReason.Canceled]:
        print("❌ No speech detected.")
        return None

# 🔍 Analyze Text with OpenAI
def analyze_text(text):
    prompt = f"""
    You are an AI assistant that extracts intents from user queries and returns a structured JSON response.
    
    **Possible Intents:**
    - "youtube_search" → If the user wants to search on YouTube (extract query).
    - "google_search" → If the user wants to search on Google (extract query).
    - "whatsapp_message" → If the user wants to send a message on WhatsApp (extract contact name and message).
    - "navigation" → If the user wants directions (extract source and destination).
    - "image_description" → If the user wants an image described or scenario described.
    - "detect_obstacles" → If the user wants to detect obstacles in a path.
    - "ocr" → If the user wants to extract text from an image (or) identify whats written or whats there.
    - "screen" → If the user wants to know whats on screen.
    - "spotify" → If the user wants to play music on Spotify.
    - "zomato" → If the user wants to order food on Zomato.
    - "rapido" → If the user wants to book a ride on Rapido.
    - "redbus" → If the user wants to book a ticket on Redbus.
    **Instructions:**
    - Extract relevant details based on the intent.
    - If intent is unclear, return `"intent": "unknown"`.
    - **Output must be valid JSON only. No extra text.**

    **Examples:**
    1. User: `"Search cricket in YouTube"`
       Output:
       ```json
       {{"intent": "youtube_search", "query": "cricket"}}
       ```
    2. User: `"Find best restaurants on Google"`
       Output:
       ```json
       {{"intent": "google_search", "query": "best restaurants"}}
       ```
    3. User: `"Send hello to Vijay Krishna on WhatsApp."`
       Output:
       ```json
       {{"intent": "whatsapp_message", "contact": "Vijay Krishna", "message": "hello"}}
       ```
    4. User: `"Navigate from Chennai to Bangalore"`
       Output:
       ```json
       {{"intent": "navigation", "source": "Chennai", "destination": "Bangalore"}}
       ```
    5. User: `"Describe whats happening"`
       Output:
       ```json
       {{"intent": "image_description"}}
       ```
    6. User: `"Detect Obstacles"`
       Output:
       ```json
       {{"intent": "detect_obstacles"}}
       ```
    7.User: `"Identify whats there"`
       Output:
       ```json
       {{"intent": "ocr"}}
       ```
    8.User: `"Whats on the screen"`
       Output:
       ```json
       {{"intent": "screen"}}
       ```
    9.User: `"Play Levitating on Spotify"`
    Output:
    ```json
    {{"intent": "spotify", "song": "Levitating"}}
    ```
    10.User: `"Order a pizza on Zomato"`
    Output:
    ```json
    {{"intent": "zomato", "food_item": "pizza"}}
    ```
    11.User: `"Book a ride to Guindy on Rapido"`
    Output:
    ```json
    {{"intent": "rapido", "destination": "Guindy"}}
    ```
    12.User: `"Book a ticket from Chennai to Bangalore on Redbus"`
    Output:
    ```json
    {{"intent": "redbus", "source": "Chennai", "destination": "Bangalore"}}
    ```
    **User Input:** "{text}"  
    """

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-pro")
    
    response = model.generate_content(prompt)

    try:
        # Ensure only JSON is parsed
        json_str = response.text.strip().strip("```json").strip("```")  # Cleanup formatting issues
        print(f"🔮 Gemini Response: {json_str}")
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError:
        print("⚠️ Error parsing Gemini response!")
        return {"intent": "unknown"}
# 📺 Search YouTube
def search_youtube(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    subprocess.run(["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url])
    print(f"✅ Opened YouTube search for: {query}")

# 🔎 Search Google
def search_google(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    subprocess.run(["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url])
    print(f"✅ Opened Google search for: {query}")

import os
import time
def book_ticket_on_redbus(source,destination):
    assistant = SmartAndroidAssistant()
    app = "redbus"
    assistant.open_app(app)
    time.sleep(7)  # Wait for the app to open

    # Tap on the search bar (Adjust coordinates as per your device)
    adb_command("input tap 259 370")  
    time.sleep(5)

    # Type the food item
    adb_command(f'input text "{source.replace(" ", "%s")}"')
    time.sleep(2)

    
    #adb_command("input keyevent 66")  
    #time.sleep(3)
    
    adb_command("input tap 298 438")
    time.sleep(2)
    
    adb_command("input tap 247 547")
    time.sleep(2)
    
    
    adb_command(f'input text "{destination.replace(" ", "%s")}"')
    time.sleep(2)

    adb_command("input tap 298 438")
    time.sleep(2)
    
    adb_command("input tap 297 872")
    time.sleep(2)
    
    adb_command("input tap 274 938")
    time.sleep(2)
    
    adb_command("input tap 287 658")
    time.sleep(2)
    
    adb_command("input tap 287 658")
    time.sleep(2)


def play_spotify_song(song_name):
    def adb_command(cmd):
        os.system(f"adb shell {cmd}")

    adb_command("am start -n com.spotify.music/.MainActivity")
    time.sleep(5)

    adb_command("input tap 264 1353")
    time.sleep(2)
    adb_command("input tap 264 1353")

    adb_command(f'input text "{song_name.replace(" ", "%s")}"')
    time.sleep(5)

    adb_command("input tap 173 226")
    time.sleep(5)
    adb_command("input tap 92 277")

    adb_command("input tap 300 1200")

    print("🎵 Now Playing:", song_name)


def adb_command(cmd):
    os.system(f"adb shell {cmd}")

# 📸 Describe Image using Azure CV
def describe_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        image_stream = io.BytesIO(image_data)
        description_results = cv_client.describe_image_in_stream(image_stream)

        if description_results.captions:
            for caption in description_results.captions:
                print(f"🖼️ Description: {caption.text} (Confidence: {caption.confidence:.2f})")
        else:
            print("⚠️ No description found.")
    except Exception as e:
        print(f"⚠️ Error describing image: {e}")
def order_food_on_zomato(food_item):
    assistant = SmartAndroidAssistant()
    app = "zomato"
    assistant.open_app(app)
    time.sleep(10)  # Wait for the app to open

    # Tap on the search bar (Adjust coordinates as per your device)
    adb_command("input tap 159 228")  
    time.sleep(2)

    # Type the food item
    adb_command(f'input text "{food_item.replace(" ", "%s")}"')
    time.sleep(2)

    # Press Enter to search
    adb_command("input keyevent 66")  
    time.sleep(3)

    # Tap on the first search result (Modify coordinates if needed)
    adb_command("input tap 167 350")
    time.sleep(3)

    # Tap on 'Add to Cart' (Modify coordinates if needed)
    adb_command("input tap 118 900")
    time.sleep(2)

    # Tap on 'Proceed to Checkout' (Modify coordinates if needed)
    adb_command("input tap 530 719")
    time.sleep(2)
    adb_command("input tap 520 702")
    # Confirm order (Modify coordinates if needed)
    adb_command("input tap 492 1321")
    adb_command("input tap 492 1321")
    print(f"✅ Ordered {food_item} on Zomato!")

# Call the function with the food item you want to order

# 📩 Open WhatsApp and Send Message
def open_whatsapp():
    subprocess.run(["adb", "shell", "am", "start", "-n", "com.whatsapp/.HomeActivity"])
    time.sleep(2)

def search_contact(contact_name):
    subprocess.run(["adb", "shell", "input", "tap", "900", "200"])  # Tap search bar
    time.sleep(1)
    
    formatted_name = contact_name.replace(" ", "%s")
    subprocess.run(["adb", "shell", "input", "text", formatted_name])
    time.sleep(2)

    subprocess.run(["adb", "shell", "input", "tap", "300", "400"])  # Select contact
    time.sleep(2)
def book_ride_on_rapido(destination):
    assistant = SmartAndroidAssistant()
    app = "rapido"
    assistant.open_app(app)
    time.sleep(6)  # Wait for the app to open

    # Tap on the search bar (Adjust coordinates as per your device)
    adb_command("input tap 211 106")  
    time.sleep(5)

    # Type the food item
    adb_command(f'input text "{destination.replace(" ", "%s")}"')
    time.sleep(2)

    
    #adb_command("input keyevent 66")  
    #time.sleep(3)
    
    adb_command("input tap 152 501")
    time.sleep(2)
    adb_command("input tap 300 1125")
    time.sleep(2)

def send_message(message):
    formatted_msg = message.replace(" ", "%s")
    subprocess.run(["adb", "shell", "input", "text", formatted_msg])
    time.sleep(1)
    subprocess.run(["adb", "shell", "input", "keyevent", "66"])  # Press Enter

# 🗺️ Start Navigation
def start_navigation(source, destination):
    data = {"source": source, "destination": destination}
    response = requests.post(FLASK_API_URL, json=data)
    
    if response.status_code == 200:
        print("✅ Navigation started successfully!")
    else:
        print(f"❌ Failed to start navigation: {response.json()}")
import os
import time

def main():
    while True:
        text = recognize_speech()
        
        if text:
            if text.lower().strip() in ["exit", "quit"]:
                print("👋 Exiting program. Goodbye!")
                break  # Exit the loop
            
            result = analyze_text(text)
            
            if result:
                intent = result.get("intent")

                if intent == "youtube_search":
                    query = result.get("query")
                    if query:
                        search_youtube(query)

                elif intent == "google_search":
                    query = result.get("query")
                    if query:
                        search_google(query)

                elif intent == "whatsapp_message":
                    contact_name = result.get("contact")
                    message = result.get("message")
                    if contact_name and message:
                        open_whatsapp()
                        search_contact(contact_name)
                        send_message(message)
                        print(f"✅ Sent WhatsApp message to {contact_name}: {message}")

                elif intent == "navigation":
                    source = result.get("source")
                    destination = result.get("destination")
                    if source and destination:
                        print(f"🗺️ Navigating from {source} to {destination}...")
                        start_navigation(source, destination)

                elif intent == "image_description":
                    os.system("python imagereg.py")

                elif intent == "ocr":
                    os.system("python ocr.py")

                elif intent == "screen":
                    os.system("python screendes.py")
                elif intent == "spotify":
                    play_spotify_song(result.get("song"))

                elif intent == "detect_obstacles":
                    os.system("python new.py")
                    print("🚧 Obstacle detection feature not implemented.")
                elif intent == "zomato":
                    food_item = result.get("food_item")
                    if food_item:
                        order_food_on_zomato(food_item)
                elif intent == "rapido":
                    destination = result.get("destination")
                    if destination:
                        book_ride_on_rapido(destination)
                elif intent == "redbus":
                    source = result.get("source")
                    destination = result.get("destination")
                    if source and destination:
                        book_ticket_on_redbus(source, destination)
                else:
                    print("⚠️ No valid intent detected.")
            else:
                print("⚠️ Failed to analyze the request.")
        else:
            print("⚠️ No speech detected. Please try again.")

        time.sleep(1)  # Small delay to prevent immediate re-trigger

if __name__ == "__main__":
    main()
