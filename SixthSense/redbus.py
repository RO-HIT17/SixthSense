import os
import time
from opener import SmartAndroidAssistant
def adb_command(cmd):
    os.system(f"adb shell {cmd}")

def book_ticket_on_redbus(source,destination):
    assistant = SmartAndroidAssistant()
    app = "redbus"
    assistant.open_app(app)
    time.sleep(6)  

    adb_command("input tap 259 370")  
    time.sleep(5)

    adb_command(f'input text "{source.replace(" ", "%s")}"')
    time.sleep(2)

    
    
    adb_command("input tap 298 438")
    time.sleep(2)
    
    adb_command("input tap 247 547")
    time.sleep(2)
    
    
    adb_command(f'input text "{destination.replace(" ", "%s")}"')
    time.sleep(2)

    adb_command("input tap 298 438")
    time.sleep(2)
    
    adb_command("input tap 297 872")
    time.sleep(2)
    
    adb_command("input tap 274 938")
    time.sleep(2)
    
    adb_command("input tap 287 658")
    time.sleep(2)
    
    adb_command("input tap 287 658")
    time.sleep(2)
    
    
book_ticket_on_redbus("Chennai","Madurai")
