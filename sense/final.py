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

# 🏁 Main Execution
if __name__ == "__main__":
    text = recognize_speech()
    if text:
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
            
            elif intent == "detect_obstacles":
                os.system("python new.py")
                print("🚧 Obstacle detection feature not implemented.")
            else:
                print("⚠️ No valid intent detected.")
        else:
            print("⚠️ Failed to analyze the request.")
