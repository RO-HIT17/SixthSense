import google.generativeai as genai
import base64
import subprocess
import re
import time

# ✅ Configure Gemini API
API_KEY = "AIzaSyDPwijZg1zvbofMjpdVogd3yABXcwP7Otc"  # Replace with your API key
genai.configure(api_key=API_KEY)

# ✅ Capture Screenshot Using ADB
def capture_screenshot(filename="whatsapp_screen.png"):
    subprocess.run(["adb", "shell", "screencap", "-p", f"/sdcard/{filename}"])
    subprocess.run(["adb", "pull", f"/sdcard/{filename}", "."])
    print(f"📸 Screenshot saved as {filename}!")

# ✅ Convert Image to Base64 for Gemini
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# ✅ Send Screenshot to Gemini Vision AI
def analyze_screenshot(image_path, query):
    image_base64 = encode_image(image_path)
    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content([
        {"text": query},
        {"inline_data": {"mime_type": "image/png", "data": image_base64}}
    ])
    
    return response.text  # Extract Gemini's response

# ✅ Extract (x, y) Coordinates from Gemini Response
def extract_coordinates(response_text, label):
    match = re.search(fr"{label} at \[(\d+), (\d+)\]", response_text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None

# ✅ Perform Tap Action via ADB
def tap_screen(coords):
    if coords:
        x, y = coords
        subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])
        print(f"👉 Tapped on {coords}")
        time.sleep(2)  # Pause for UI to update
    else:
        print("⚠️ No coordinates found!")

# ✅ Automate Replying to a Chat
def send_whatsapp_reply(message):
    # Tap on the message input field
    tap_screen(message_input_coords)

    # Type the message
    subprocess.run(["adb", "shell", "input", "text", message])

    # Press Enter to send
    subprocess.run(["adb", "shell", "input", "keyevent", "66"])
    print("📩 Message sent!")

# ✅ Open unread messages and extract the last message
def read_last_message():
    # Take screenshot of the open chat
    capture_screenshot("open_chat.png")

    # Analyze the open chat for the last received message
    last_message = analyze_screenshot("open_chat.png", "Extract the last received message in this chat.")
    
    print(f"🗨️ Last received message: {last_message}")
    return last_message

# 🚀 Main Execution Flow
if __name__ == "__main__":
    capture_screenshot()
    ui_analysis = analyze_screenshot("whatsapp_screen.png", "Analyze this WhatsApp screenshot and find UI elements like unread messages, chat buttons, and the message input field.")
    print("🔍 UI Analysis Result:\n", ui_analysis)

    # Extract coordinates from AI response
    unread_coords = extract_coordinates(ui_analysis, "Unread messages")
    chat_button_coords = extract_coordinates(ui_analysis, "Chat button")
    message_input_coords = extract_coordinates(ui_analysis, "Message input field")

    print(f"📍 Unread Message at: {unread_coords}")
    print(f"📍 Chat Button at: {chat_button_coords}")
    print(f"📍 Message Input at: {message_input_coords}")

    # Open unread messages and read the last message
    if unread_coords:
        tap_screen(unread_coords)  # Open unread chat
        time.sleep(3)  # Wait for chat to open
        last_msg = read_last_message()

        # (Optional) Reply automatically based on message
        send_whatsapp_reply(f"Hey! I saw your message: {last_msg[:20]}...")  # Send first 20 chars as preview
    else:
        print("✅ No unread messages found.")
