import os
import time

# Define song name (Modify this)
SONG_NAME = "Levitating"  # Change to your desired song

# Coordinates for Spotify search bar (Update these after finding them using getevent or screencap method)
SEARCH_X, SEARCH_Y = 500, 600  # Update these coordinates

# Coordinates for the first search result (Modify if needed)
RESULT_X, RESULT_Y = 500, 900  # Update these coordinates

# Coordinates for the play button (Modify if needed)
PLAY_X, PLAY_Y = 300, 1200  # Update these coordinates

# Function to execute ADB commands
def adb_command(cmd):
    os.system(f"adb shell {cmd}")

# Step 1: Launch Spotify
adb_command("am start -n com.spotify.music/.MainActivity")
time.sleep(5)  # Wait for app to open

# Step 2: Tap on the search bar
adb_command(f"input tap 264 1353")
time.sleep(2)
adb_command(f"input tap 264 1353")
# Step 3: Type the song name
#formatted_msg = message.replace(" ", "%s")
adb_command(f'input text "{SONG_NAME.replace(" ", "%s")}"')
time.sleep(2)

# Step 4: Tap on the first result
adb_command(f"input tap 173 226")
time.sleep(3)
adb_command(f"input tap 92 277")
# Step 5: Tap the play button
adb_command(f"input tap {PLAY_X} {PLAY_Y}")

print("🎵 Now Playing:", SONG_NAME)
