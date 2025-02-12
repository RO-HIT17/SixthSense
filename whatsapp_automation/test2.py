import os
import time
import cv2
import numpy as np
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from dotenv import load_dotenv

KEY = os.getenv("AZURE_COMPUTERVISION_KEY")
ENDPOINT = os.getenv("AZURE_COMPUTERVISION_ENDPOINT")

computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def take_screenshot():
    try:
        os.system("adb shell screencap -p /sdcard/screen.png")
        os.system("adb pull /sdcard/screen.png .")
        return True
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
        return False

def crop_chat_area(image_path="screen.png"):
    image = cv2.imread(image_path)
    if image is None:
        print("❌ Failed to load image for cropping")
        return image_path  

    height, width, _ = image.shape
    cropped = image[int(height * 0.4):height, 0:width]  

    cropped_path = "cropped_screen.png"
    cv2.imwrite(cropped_path, cropped)
    print("📸 Cropped chat area saved!")
    return cropped_path

def get_unread_chat_positions(image_path="screen.png"):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise Exception("Failed to load image")

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_green = np.array([40, 100, 100])
        upper_green = np.array([80, 255, 255])

        mask = cv2.inRange(hsv, lower_green, upper_green)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        unread_positions = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if 15 < w < 50 and 15 < h < 50:  
                chat_y = y + h // 2  
                chat_x = x + 250  
                unread_positions.append((chat_x, chat_y))

                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imwrite('debug_detection.png', image)
        return unread_positions

    except Exception as e:
        print(f"⚠️ Error detecting unread chats: {e}")
        return []

def tap(x, y):
    try:
        os.system(f"adb shell input tap {x} {y}")
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Tap failed: {e}")

def read_last_message():
    try:
        take_screenshot()
        cropped_image = crop_chat_area()

        with open(cropped_image, "rb") as image_stream:
            image_data = image_stream.read()

        print("📤 Sending image to Azure OCR...")
        read_response = computervision_client.read_in_stream(image_data, raw=True)

        read_operation_location = read_response.headers.get("Operation-Location")
        if not read_operation_location:
            print("❌ Azure OCR: No 'Operation-Location' found in response!")
            return ""

        operation_id = read_operation_location.split("/")[-1]

        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status.lower() not in ['notstarted', 'running']:
                break
            print("⏳ Waiting for OCR to process...")
            time.sleep(1)

        if read_result.status == OperationStatusCodes.succeeded:
            text_results = [line.text for text_result in read_result.analyze_result.read_results for line in text_result.lines]

            print("📜 Detected Text:\n", "\n".join(text_results))
            return "\n".join(text_results)

        print("❌ Failed to read text from image")
        return ""

    except Exception as e:
        print(f"🚨 OCR Error: {e}")
        return ""

def get_last_message_via_clipboard():
    try:
        os.system("adb shell input touchscreen swipe 500 1600 500 400")  
        os.system("adb shell input tap 500 1600")  
        os.system("adb shell am broadcast -a clipper.get")  
        time.sleep(1)

        result = os.popen("adb shell am broadcast -a clipper.get").read()
        print(f"📋 Clipboard Text Extracted: {result}")
        return result

    except Exception as e:
        print(f"⚠️ Clipboard extraction failed: {e}")
        return ""

def process_whatsapp_unread():
    print("🚀 Starting WhatsApp automation...")

    while True:
        if not take_screenshot():
            print("❌ Screenshot failed. Check device connection.")
            break

        unread_positions = get_unread_chat_positions()
        if not unread_positions:
            print("✅ No unread messages found.")
            break

        print(f"🔍 Found {len(unread_positions)} unread chats.")

        for idx, (x, y) in enumerate(unread_positions, 1):
            print(f"\n📩 Processing chat {idx}/{len(unread_positions)}")

            tap(x, y)  
            time.sleep(2)

            message = get_last_message_via_clipboard().strip()
            if not message:
                print("⚠️ Clipboard extraction failed. Using Azure OCR...")
                message = read_last_message()

            print(f"📜 Last message: {message}")

            os.system("adb shell input keyevent KEYCODE_BACK")  
            time.sleep(1.5)

        print("\n🎯 Finished processing all unread chats.")
        break

if __name__ == "__main__":
    result = os.popen("adb devices").read()
    if "device" not in result:
        print("❌ No device connected. Please connect an Android device.")
    else:
        process_whatsapp_unread()
