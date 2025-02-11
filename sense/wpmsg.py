import google.generativeai as genai
import base64
import subprocess
import json
import pyttsx3
import time
import os
import re
# ✅ Configure Gemini API (Use environment variable for security)
API_KEY = "AIzaSyDPwijZg1zvbofMjpdVogd3yABXcwP7Otc"  # Set this in your environment variable
if not API_KEY:
    raise ValueError("❌ API Key not found! Set GEMINI_API_KEY in your environment variables.")

genai.configure(api_key=API_KEY)

# ✅ Capture Screenshot Using ADB
def capture_screenshot():
    subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/whatsapp_screen.png"])
    subprocess.run(["adb", "pull", "/sdcard/whatsapp_screen.png", "."])
    print("📸 Screenshot captured!")

# ✅ Convert Image to Base64 for Gemini
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# ✅ Send Screenshot to Gemini Vision AI
def analyze_screenshot():
    image_base64 = encode_image("whatsapp_screen.png")
    model = genai.GenerativeModel('gemini-2.0-flash')  # Use the latest stable vision model

    response = model.generate_content([
        {"text": (
            "You are an AI that extracts structured data from WhatsApp screenshots. "
            "Return ONLY a JSON array in this format:\n"
            '[{"contact": "Name", "unread_count": Number}, {"contact": "Another Name", "unread_count": Number}]\n\n'
            "Instructions:\n"
            "1. Identify contacts with unread messages.\n"
            "2. Count the number of unread messages for each contact.\n"
            "3. Return ONLY a valid JSON array. Do NOT return explanations, markdown, or additional text."
        )},
        {"inline_data": {"mime_type": "image/png", "data": image_base64}}
    ])
    response_text = response.text.strip()
    return extract_json(response_text) 
    
def extract_json(response_text):
    try:
        # ✅ Extract JSON using regex (handles extra text issues)
        match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if match:
            json_text = match.group(0)
            return json.loads(json_text)  # ✅ Convert to Python List
        else:
            print("⚠️ No valid JSON found in the response.")
            return []
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format received.")
        return []
# ✅ Text-to-Speech (TTS) Announcement
def speak_unread_messages(unread_messages):
    engine = pyttsx3.init()

    if unread_messages:
        for msg in unread_messages:
            text = f"{msg['contact']} has {msg['unread_count']} unread messages."
            print("🔊 Speaking:", text)
            engine.say(text)
            engine.runAndWait()

        engine.runAndWait()
    else:
        print("✅ No unread messages.")
        engine.say("No unread messages.")
        engine.runAndWait()

# ✅ Print & Speak the Unread Messages
    if unread_messages:
        print("📥 Unread Messages Found:")
        for msg in unread_messages:
            print(f"📍 {msg['contact']} - {msg['unread_count']} unread messages")

    speak_unread_messages(unread_messages)

# ✅ Extract Unread Messages from Gemini Response

# ✅ Text-to-Speech (TTS) Announcement
def speak_unread_messages(unread_messages):
    engine = pyttsx3.init()

    if unread_messages:
        for msg in unread_messages:
            text = f"{msg['contact']} has {msg['unread_count']} unread messages."
            print("🔊 Speaking:", text)
            engine.say(text)
            engine.runAndWait()
    else:
        print("✅ No unread messages.")
        engine.say("No unread messages.")
        engine.runAndWait()

# 🚀 Main Execution Flow
if __name__ == "__main__":
    capture_screenshot()
    time.sleep(2)  # Allow time for image capture

    unread_messages = analyze_screenshot()
    
    if unread_messages:
        print("📥 Unread Messages Found:")
        for msg in unread_messages:
            print(f"📍 {msg['contact']} - {msg['unread_count']} unread messages")

    speak_unread_messages(unread_messages)
