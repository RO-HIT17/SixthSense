import cv2
import os
import io
import time
import pyttsx3  # 🔊 Text-to-Speech
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

# 🔑 Azure Computer Vision Credentials
VISION_API_KEY = "6a2U9CnbPO2JqPY9Doi5LEVemTW0F5jI6nVnFg0Td1JGCvGCi2l0JQQJ99BBACYeBjFXJ3w3AAAFACOGC0BT"
VISION_ENDPOINT = "https://horizon-test1711.cognitiveservices.azure.com/"

# 🎙️ Initialize Text-to-Speech Engine
tts_engine = pyttsx3.init()

# 🔍 Create Computer Vision Client
vision_client = ComputerVisionClient(VISION_ENDPOINT, CognitiveServicesCredentials(VISION_API_KEY))

# 🎥 Capture Image from External Camera
cap = cv2.VideoCapture(1)  # Use external camera
if not cap.isOpened():
    print("❌ Error: Could not open external camera.")
    exit()

ret, frame = cap.read()
if not ret:
    print("❌ Error: Could not capture frame.")
    cap.release()
    exit()

# 📸 Save Captured Image
image_path = "captured_image.jpg"
cv2.imwrite(image_path, frame)
cap.release()
cv2.destroyAllWindows()

print(f"✅ Image captured and saved as {image_path}")

# 🔍 Perform OCR (Text Extraction)
with open(image_path, "rb") as image:
    ocr_result = vision_client.read_in_stream(image, raw=True)

# 🔄 Get the operation ID
operation_location = ocr_result.headers["Operation-Location"]
operation_id = operation_location.split("/")[-1]

# ⏳ Wait for Processing
while True:
    result = vision_client.get_read_result(operation_id)
    if result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
        break
    time.sleep(1)

# 📖 Extract and Speak Text
extracted_text = ""
if result.status == OperationStatusCodes.succeeded:
    for page in result.analyze_result.read_results:
        for line in page.lines:
            extracted_text += line.text + " "
    print("\n📖 Extracted Text:\n", extracted_text)

    # 🗣️ Speak the Extracted Text
    if extracted_text.strip():
        print("\n🎙️ Speaking the extracted text...")
        tts_engine.say(extracted_text)
        tts_engine.runAndWait()
    else:
        print("\n⚠️ No text detected in the image.")
else:
    print("\n❌ OCR Failed.")
