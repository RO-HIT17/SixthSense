import subprocess
import time

# Function to run ADB command
def run_adb_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr.decode()}")
    return result.stdout.decode()

# Step 1: Open WhatsApp contact/chat
def search_contact(contact_name):
    subprocess.run(["adb", "shell", "input", "tap", "900", "200"])  # Tap search bar (adjust coordinates if needed)
    time.sleep(1)
    
    formatted_name = contact_name.replace(" ", "%s")  # Handle spaces for ADB input
    subprocess.run(["adb", "shell", "input", "text", formatted_name])
    time.sleep(2)

    subprocess.run(["adb", "shell", "input", "tap", "300", "400"])  # Adjust if needed
    time.sleep(2)

def tap_microphone_button():
    command = "adb shell input swipe 666 1371 666 1371 5000"  # Replace with your actual coordinates
    run_adb_command(command)
    time.sleep(5)  # Wait for the microphone to start recording

def send_voice_message(contact_number):
    print("📱 Opening WhatsApp...")
    """Launch WhatsApp."""
    subprocess.run(["adb", "shell", "am", "start", "-n", "com.whatsapp/.HomeActivity"])
    time.sleep(2)  

    search_contact(contact_number)
    
    print("🎤 Recording voice message...")
    tap_microphone_button()
    
    print("✅ Voice message sent successfully!")

# Run the script
if __name__ == "__main__":
    contact_name = "Vijay Krishna"  
    send_voice_message(contact_name)
