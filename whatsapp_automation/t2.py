import google.generativeai as genai
import base64
import subprocess
import re
import time
from dotenv import load_dotenv
import os
API_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key=API_KEY)

def capture_screenshot(filename="whatsapp_screen.png"):
    subprocess.run(["adb", "shell", "screencap", "-p", f"/sdcard/{filename}"])
    subprocess.run(["adb", "pull", f"/sdcard/{filename}", "."])
    print(f"📸 Screenshot saved as {filename}!")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_screenshot(image_path, query):
    image_base64 = encode_image(image_path)
    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content([
        {"text": query},
        {"inline_data": {"mime_type": "image/png", "data": image_base64}}
    ])
    
    return response.text  

def extract_coordinates(response_text, label):
    match = re.search(fr"{label} at \[(\d+), (\d+)\]", response_text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None

def tap_screen(coords):
    if coords:
        x, y = coords
        subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])
        print(f"👉 Tapped on {coords}")
        time.sleep(2)  
    else:
        print("⚠️ No coordinates found!")

def send_whatsapp_reply(message):
    tap_screen(message_input_coords)

    subprocess.run(["adb", "shell", "input", "text", message])

    subprocess.run(["adb", "shell", "input", "keyevent", "66"])
    print("📩 Message sent!")

def read_last_message():
    capture_screenshot("open_chat.png")

    last_message = analyze_screenshot("open_chat.png", "Extract the last received message in this chat.")
    
    print(f"🗨️ Last received message: {last_message}")
    return last_message

if __name__ == "__main__":
    capture_screenshot()
    ui_analysis = analyze_screenshot("whatsapp_screen.png", "Analyze this WhatsApp screenshot and find UI elements like unread messages, chat buttons, and the message input field.")
    print("🔍 UI Analysis Result:\n", ui_analysis)

    unread_coords = extract_coordinates(ui_analysis, "Unread messages")
    chat_button_coords = extract_coordinates(ui_analysis, "Chat button")
    message_input_coords = extract_coordinates(ui_analysis, "Message input field")

    print(f"📍 Unread Message at: {unread_coords}")
    print(f"📍 Chat Button at: {chat_button_coords}")
    print(f"📍 Message Input at: {message_input_coords}")

    if unread_coords:
        tap_screen(unread_coords)  
        time.sleep(3)  
        last_msg = read_last_message()

        send_whatsapp_reply(f"Hey! I saw your message: {last_msg[:20]}...")  
    else:
        print("✅ No unread messages found.")
