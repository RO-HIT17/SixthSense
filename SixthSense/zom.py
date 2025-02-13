import os
import time
from opener import SmartAndroidAssistant
def adb_command(cmd):
    os.system(f"adb shell {cmd}")

def order_food_on_zomato(food_item):
    assistant = SmartAndroidAssistant()
    app = "zomato"
    assistant.open_app(app)
    time.sleep(6)

    adb_command("input tap 159 228")  
    time.sleep(2)

    adb_command(f'input text "{food_item.replace(" ", "%s")}"')
    time.sleep(2)

    time.sleep(3)

    adb_command("input tap 167 350")
    time.sleep(3)

    adb_command("input tap 118 900")
    time.sleep(2)

    adb_command("input tap 530 719")
    time.sleep(2)
    adb_command("input tap 520 702")
    adb_command("input tap 492 1321")
    adb_command("input tap 492 1321")
    print(f"✅ Ordered {food_item} on Zomato!")

order_food_on_zomato("Burger")
