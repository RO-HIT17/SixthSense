import os
import io
import time
import pyttsx3
import cv2
import subprocess  
from PIL import Image
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# 🔑 Azure Computer Vision Credentials
AZURE_ENDPOINT = os.getenv("AZURE_COMPUTERVISION_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_COMPUTERVISION_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

tts_engine = pyttsx3.init()
screenshot_path = "mobile_screenshot.png"

try:
    print("📸 Capturing screenshot from mobile...")
    subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screenshot.png"])
    subprocess.run(["adb", "pull", "/sdcard/screenshot.png", screenshot_path])
    print(f"✅ Screenshot saved as {screenshot_path}")
except Exception as e:
    print(f"❌ Error capturing screenshot: {e}")
    exit()

with open(screenshot_path, "rb") as image_file:
    image_data = image_file.read()

image_stream = io.BytesIO(image_data)  

client = ComputerVisionClient(AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_KEY))
description_results = client.describe_image_in_stream(image_stream)

if description_results.captions:
    for caption in description_results.captions:
        description_text = caption.text
        print(f"📝 Description: {caption.text} (Confidence: {caption.confidence:.2f})")
else:
    description_text = "No description found."
    print("❌ No description found.")

if description_text != "No description found.":

    prompt = f"""
    Describe the following mobile screen:

    Screenshot Description: "{description_text}"

    Provide 2-3 lines description of the screen contents.
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    expanded_description = response.text if response.text else "Failed to generate an expanded description."
    print("\n🔹 **Expanded Description:**\n", expanded_description)
else:
    expanded_description = "No valid image description available for expansion."

if expanded_description.strip() and expanded_description != "No valid image description available for expansion.":
    print("\n🎙️ Speaking the expanded description...")
    tts_engine.say(expanded_description)
    tts_engine.runAndWait()
else:
    print("\n⚠️ No valid text to speak.")
