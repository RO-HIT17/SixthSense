import subprocess
import time

def run_adb_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr.decode()}")
    return result.stdout.decode()

def search_contact(contact_name):
    subprocess.run(["adb", "shell", "input", "tap", "900", "200"])  
    time.sleep(1)
    
    formatted_name = contact_name.replace(" ", "%s")  
    subprocess.run(["adb", "shell", "input", "text", formatted_name])
    time.sleep(2)

    subprocess.run(["adb", "shell", "input", "tap", "300", "400"])  
    time.sleep(2)

def tap_microphone_button():
    command = "adb shell input swipe 666 1371 666 1371 5000"  
    run_adb_command(command)
    time.sleep(5)  

def send_voice_message(contact_number):
    print("📱 Opening WhatsApp...")
    subprocess.run(["adb", "shell", "am", "start", "-n", "com.whatsapp/.HomeActivity"])
    time.sleep(2)  

    search_contact(contact_number)
    
    print("🎤 Recording voice message...")
    tap_microphone_button()
    
    print("✅ Voice message sent successfully!")

if __name__ == "__main__":
    contact_name = "Vijay Krishna"  
    send_voice_message(contact_name)
