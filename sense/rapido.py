import os
import time
from opener import SmartAndroidAssistant
def adb_command(cmd):
    os.system(f"adb shell {cmd}")

def book_ride_on_rapido(destination):
    assistant = SmartAndroidAssistant()
    app = "rapido"
    assistant.open_app(app)
    time.sleep(6)  # Wait for the app to open

    # Tap on the search bar (Adjust coordinates as per your device)
    adb_command("input tap 211 106")  
    time.sleep(5)

    # Type the food item
    adb_command(f'input text "{destination.replace(" ", "%s")}"')
    time.sleep(2)

    
    #adb_command("input keyevent 66")  
    #time.sleep(3)
    
    adb_command("input tap 152 501")
    #time.sleep(2)
    adb_command("input tap 300 1125")
    time.sleep(2)
    # Tap on 'Proceed to Checkout' (Modify coordinates if needed)
    #adb_command("input tap 306 1134")
    #time.sleep(2)
    #adb_command("input tap 285 1106")
    #print(f"✅ Ordered {destination} on Zomato!")
    #adb_command("input tap 285 1106")
     
# Call the function with the food item you want to order
book_ride_on_rapido("Guindy")
