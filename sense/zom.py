import os
import time
from opener import SmartAndroidAssistant
def adb_command(cmd):
    os.system(f"adb shell {cmd}")

def order_food_on_zomato(food_item):
    assistant = SmartAndroidAssistant()
    app = "zomato"
    assistant.open_app(app)
    time.sleep(6)  # Wait for the app to open

    # Tap on the search bar (Adjust coordinates as per your device)
    adb_command("input tap 159 228")  
    time.sleep(2)

    # Type the food item
    adb_command(f'input text "{food_item.replace(" ", "%s")}"')
    time.sleep(2)

    # Press Enter to search
    #adb_command("input keyevent 66")  
    time.sleep(3)

    # Tap on the first search result (Modify coordinates if needed)
    adb_command("input tap 167 350")
    time.sleep(3)

    # Tap on 'Add to Cart' (Modify coordinates if needed)
    adb_command("input tap 118 900")
    time.sleep(2)

    # Tap on 'Proceed to Checkout' (Modify coordinates if needed)
    adb_command("input tap 530 719")
    time.sleep(2)
    adb_command("input tap 520 702")
    # Confirm order (Modify coordinates if needed)
    adb_command("input tap 492 1321")
    adb_command("input tap 492 1321")
    print(f"✅ Ordered {food_item} on Zomato!")

# Call the function with the food item you want to order
order_food_on_zomato("Burger")
