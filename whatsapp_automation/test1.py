import os
import time
import cv2
import pytesseract
import numpy as np

# Take a screenshot and pull it to PC
def take_screenshot():
    os.system("adb shell screencap -p /sdcard/screen.png")
    os.system("adb pull /sdcard/screen.png")

# Detect unread message badges
def get_unread_badge_positions(image_path="screen.png"):
    image = cv2.imread(image_path)

    # Define WhatsApp unread badge color range (green)
    lower_green = np.array([50, 200, 50])
    upper_green = np.array([100, 255, 100])

    mask = cv2.inRange(image, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    unread_positions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 20 < w < 100 and 20 < h < 100:  # Filtering out small noise
            unread_positions.append((x + w // 2, y + h // 2))  # Click at badge center

    return unread_positions

# Tap directly on the unread badge
def tap(x, y):
    os.system(f"adb shell input tap {x} {y}")

# Swipe up inside a chat (for long messages)
def swipe_up():
    os.system("adb shell input swipe 500 1500 500 500")

# Extract last message from chat using OCR
def read_last_message():
    take_screenshot()
    img = cv2.imread("screen.png")

    # Focus OCR on bottom 40% of the screen (last messages area)
    h, w, _ = img.shape
    cropped_img = img[int(h * 0.6):, :]

    # Extract text using Tesseract OCR
    text = pytesseract.image_to_string(cropped_img, lang="eng")

    return text.strip()

# Main loop: Click badges, open chats, read messages, return to chat list
def process_whatsapp_unread():
    while True:
        take_screenshot()
        unread_positions = get_unread_badge_positions()

        if not unread_positions:
            print("✅ No unread messages found.")
            break

        print(f"🔍 Found {len(unread_positions)} unread chats. Opening them one by one...")

        for x, y in unread_positions:
            tap(x, y)  # Click on unread badge
            time.sleep(2)  # Wait for chat to open

            # Swipe up to capture long messages
            swipe_up()
            time.sleep(1)

            message = read_last_message()
            print(f"📩 New message: {message}")

            time.sleep(1)
            os.system("adb shell input keyevent 4")  # Press back button
            time.sleep(1)

if __name__ == "__main__":
    process_whatsapp_unread()
