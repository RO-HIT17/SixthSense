import cv2
import os
import io
import time
import pyttsx3  
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import google.generativeai as genai
from dotenv import load_dotenv

AZURE_ENDPOINT = os.getenv("AZURE_COMPUTERVISION_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_COMPUTERVISION_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  

client = ComputerVisionClient(AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_KEY))

cap = cv2.VideoCapture(1)  
if not cap.isOpened():
    print("❌ Error: Could not open external camera.")
    exit()

ret, frame = cap.read()
if not ret:
    print("❌ Error: Could not capture frame.")
    cap.release()
    exit()

image_path = "captured_image.jpg"
cv2.imwrite(image_path, frame)
cap.release()
cv2.destroyAllWindows()

print(f"✅ Image captured and saved as {image_path}")

with open(image_path, "rb") as image_file:
    image_data = image_file.read()

image_stream = io.BytesIO(image_data)  

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
    Expand on the following image description with 1 lines, adding context, and possible background information but dont change the original meaning:

    Description: "{description_text}"

    Make it informative, and detailed.
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
