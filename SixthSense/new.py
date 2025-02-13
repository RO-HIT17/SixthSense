import cv2
import numpy as np
import pyttsx3
import time
import os
from ultralytics import YOLO
import google.generativeai as genai
from dotenv import load_dotenv

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def expand_image_description(warning):
    prompt = f"""
    Expand on the following warning message in a line for the navigation of blind people 
    (sometimes instead of cm use meters/feet) mention distance in any one scale:
    Description: "{warning}"
    """
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    expanded_description = response.text if response.text else "Failed to generate an expanded description."
    print("\n🔹 **Expanded Description:**\n", expanded_description)   
    engine.say(expanded_description)
    engine.runAndWait()

engine = pyttsx3.init()
engine.setProperty('rate', 150)  

model = YOLO("yolov8n.pt")

KNOWN_WIDTHS = {
    "person": 40, "bicycle": 65, "car": 150, "motorbike": 70, "bus": 250,
    "truck": 250, "chair": 100, "laptop": 40, "cell phone": 15
}

CRITICAL_DISTANCES = {
    "person": 50,    
    "laptop": 40,    
    "chair": 300,    
}

GENERAL_CRITICAL_DISTANCE = 100  
FOCAL_LENGTH = 150  

cap = cv2.VideoCapture(1)  
last_update_time = time.time()
distance_results = {}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    
    results = model(frame)
    detected_objects = {}
    warnings = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = model.names[int(box.cls[0])]
            confidence = box.conf[0].item()

            if label not in KNOWN_WIDTHS:
                continue  

            width_px = x2 - x1  
            real_width = KNOWN_WIDTHS[label]  
            distance = (real_width * FOCAL_LENGTH) / width_px  

            if label not in detected_objects:
                detected_objects[label] = []
            detected_objects[label].append(distance)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            distance_text = f"{label} {distance:.2f} cm"
            cv2.putText(frame, distance_text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if time.time() - last_update_time >= 5:
        for label, distances in detected_objects.items():
            avg_distance = np.mean(distances)
            distance_results[label] = avg_distance

            critical_distance = CRITICAL_DISTANCES.get(label, GENERAL_CRITICAL_DISTANCE)

            if avg_distance < critical_distance:
                warning_msg = f"Warning! {label} is too close: {avg_distance:.2f} cm"
                warnings.append(warning_msg)
        
        last_update_time = time.time()

    for warning in warnings:
        expand_image_description(warning)
        
    cv2.imshow("YOLOv8 Distance Estimation", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
