import os
import time
import cv2
import pytesseract
import numpy as np

def take_screenshot():
    os.system("adb shell screencap -p /sdcard/screen.png")
    os.system("adb pull /sdcard/screen.png")

def get_unread_chat_positions(image_path="screen.png"):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    lower_green = np.array([50, 200, 50])
    upper_green = np.array([100, 255, 100])
    
    mask = cv2.inRange(image, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    unread_positions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 20 < w < 100 and 20 < h < 100:  
            unread_positions.append((x, y))

    return unread_positions

def tap(x, y):
    os.system(f"adb shell input tap {x} {y}")

def swipe_up():
    os.system("adb shell input swipe 500 1500 500 500")

def read_last_message():
    take_screenshot()
    img = cv2.imread("screen.png")
    
    text = pytesseract.image_to_string(img, lang="eng")
    
    return text.strip()

CHAT_NAME_REGION = (100, 100, 400, 150)  
LAST_MSG_REGION = (100, 150, 400, 200)   

def extract_chat_name(image):
    chat_region = image[CHAT_NAME_REGION[1]:CHAT_NAME_REGION[3], 
                       CHAT_NAME_REGION[0]:CHAT_NAME_REGION[2]]
    gray = cv2.cvtColor(chat_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    return pytesseract.image_to_string(thresh).strip()

def extract_last_message(image):
    msg_region = image[LAST_MSG_REGION[1]:LAST_MSG_REGION[3], 
                      LAST_MSG_REGION[0]:LAST_MSG_REGION[2]]
    gray = cv2.cvtColor(msg_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    return pytesseract.image_to_string(thresh).strip()

def process_whatsapp_unread():
    while True:
        take_screenshot()
        unread_positions = get_unread_chat_positions()

        if not unread_positions:
            print("✅ No unread messages found.")
            break

        print(f"🔍 Found {len(unread_positions)} unread chats.")

        for x, y in unread_positions:
            tap(x, y)  
            time.sleep(2)  
            
            take_screenshot()
            img = cv2.imread("screen.png")
            
            chat_name = extract_chat_name(img)
            last_message = extract_last_message(img)
            
            print(f"👤 Chat: {chat_name}")
            print(f"💬 Last Message: {last_message}")
            print("-" * 50)

            time.sleep(1)
            os.system("adb shell input keyevent 4")  
            time.sleep(1)

if __name__ == "__main__":
    process_whatsapp_unread()
