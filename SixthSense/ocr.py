import cv2
import os
import io
import time
import pyttsx3  
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from dotenv import load_dotenv
load_dotenv()

VISION_API_KEY = os.getenv("AZURE_COMPUTERVISION_KEY")
VISION_ENDPOINT = os.getenv("AZURE_COMPUTERVISION_ENDPOINT")

tts_engine = pyttsx3.init()

vision_client = ComputerVisionClient(VISION_ENDPOINT, CognitiveServicesCredentials(VISION_API_KEY))

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

with open(image_path, "rb") as image:
    ocr_result = vision_client.read_in_stream(image, raw=True)

# 🔄 Get the operation ID
operation_location = ocr_result.headers["Operation-Location"]
operation_id = operation_location.split("/")[-1]

while True:
    result = vision_client.get_read_result(operation_id)
    if result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
        break
    time.sleep(1)

extracted_text = ""
if result.status == OperationStatusCodes.succeeded:
    for page in result.analyze_result.read_results:
        for line in page.lines:
            if line.text!="iVCam":
                extracted_text += line.text + " "
    print("\n📖 Extracted Text:\n", extracted_text)

    if extracted_text.strip():
        print("\n🎙️ Speaking the extracted text...")
        tts_engine.say(extracted_text)
        tts_engine.runAndWait()
    else:
        print("\n⚠️ No text detected in the image.")
else:
    print("\n❌ OCR Failed.")
