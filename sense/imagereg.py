import cv2
import os
import io
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

# 🔑 Azure CV Credentials
AZURE_ENDPOINT = "https://horizon-test1711.cognitiveservices.azure.com/"
AZURE_KEY = "6a2U9CnbPO2JqPY9Doi5LEVemTW0F5jI6nVnFg0Td1JGCvGCi2l0JQQJ99BBACYeBjFXJ3w3AAAFACOGC0BT"

# ✅ Initialize the Computer Vision Client
client = ComputerVisionClient(AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_KEY))

# 🎥 Capture Image from Camera
cap = cv2.VideoCapture(1)  # Use external camera
if not cap.isOpened():
    print("❌ Error: Could not open external camera.")
    exit()

ret, frame = cap.read()
if not ret:
    print("❌ Error: Could not capture frame.")
    cap.release()
    exit()

# 📸 Save the captured image
image_path = "captured_image.jpg"
cv2.imwrite(image_path, frame)
cap.release()
cv2.destroyAllWindows()

print(f"✅ Image captured and saved as {image_path}")

# 🔍 Read the saved image
with open(image_path, "rb") as image_file:
    image_data = image_file.read()

image_stream = io.BytesIO(image_data)  # Convert bytes to a file-like object

# 📊 Call Azure CV to describe the image
description_results = client.describe_image_in_stream(image_stream)

# 📝 Print the best caption
if description_results.captions:
    for caption in description_results.captions:
        print(f"📝 Description: {caption.text} (Confidence: {caption.confidence:.2f})")
else:
    print("❌ No description found.")
