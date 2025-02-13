import os
import time

SONG_NAME = "Tum Sath Ho"  
SEARCH_X, SEARCH_Y = 500, 600  
RESULT_X, RESULT_Y = 500, 900  
PLAY_X, PLAY_Y = 300, 1200  
def adb_command(cmd):
    os.system(f"adb shell {cmd}")

adb_command("am start -n com.spotify.music/.MainActivity")
time.sleep(5)  

adb_command(f"input tap 264 1353")
time.sleep(2)
adb_command(f"input tap 264 1353")
adb_command(f'input text "{SONG_NAME.replace(" ", "%s")}"')
time.sleep(2)

adb_command(f"input tap 173 226")
time.sleep(3)
adb_command(f"input tap 92 277")
adb_command(f"input tap {PLAY_X} {PLAY_Y}")

print("🎵 Now Playing:", SONG_NAME)
