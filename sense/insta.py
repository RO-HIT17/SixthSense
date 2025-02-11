import os
import time
from opener import SmartAndroidAssistant
def adb_command(cmd):
    os.system(f"adb shell {cmd}")

def insta():
    assistant = SmartAndroidAssistant()
    app = "instagram"
    assistant.open_app(app)
    time.sleep(5)  # Wait for the app to open

    adb_command(f"input tap 128 274")
    time.sleep(2)
    adb_command(f"input tap 79 575")
    time.sleep(2)
    adb_command(f"input tap 315 1122")
    time.sleep(2)
insta()