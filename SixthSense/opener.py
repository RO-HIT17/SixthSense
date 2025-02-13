import subprocess
import time
import google.generativeai as genai
from fuzzywuzzy import process
import re
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

class SmartAndroidAssistant:
    def __init__(self):
        self.common_apps = {
            'whatsapp': {
                'package': 'com.whatsapp',
                'activity': '.Main',
                'alternatives': ['.HomeActivity', '.MainApplication']
            },
            'instagram': {
                'package': 'com.instagram.android',
                'activity': '.activity.MainTabActivity',
                'alternatives': ['.MainTabActivity', '.MainActivity']
            },
            'camera': {
                'package': 'com.android.camera',  
                'activity': '.MainActivity',
                'alternatives': ['.CameraActivity']
            },
            'camera2': {
                'package': 'com.android.camera2',  
                'activity': '.MainActivity',
                'alternatives': ['.CameraActivity']
            },
            'settings': {
                'package': 'com.android.settings',
                'activity': '.Settings',
                'alternatives': ['.MainSettings']
            },
            'phone': {
                'package': 'com.android.dialer',
                'activity': '.DialtactsActivity',
                'alternatives': ['.MainDialer']
            },
            'messages': {
                'package': 'com.android.messaging',
                'activity': '.ui.ConversationListActivity',
                'alternatives': ['.MainMessaging']
            },
            'gallery': {
                'package': 'com.android.gallery3d',
                'activity': '.app.GalleryActivity',
                'alternatives': ['.MainGallery']
            },
            'chrome': {
                'package': 'com.android.chrome',
                'activity': '.Main',
                'alternatives': ['.MainActivity']
            },
            'youtube': {
                'package': 'com.google.android.youtube',
                'activity': '.app.honeycomb.Shell$HomeActivity',
                'alternatives': ['.MainActivity']
            },
            'maps': {
                'package': 'com.google.android.apps.maps',
                'activity': '.MapsActivity',
                'alternatives': ['.MainActivity']
            },
            'playstore': {
                'package': 'com.android.vending',
                'activity': '.AssetBrowserActivity',
                'alternatives': ['.MainActivity']
            }
        }
        
        self.camera_package = self.find_camera_package()
        if self.camera_package:
            self.common_apps['camera']['package'] = self.camera_package
        
        self.installed_apps = self.get_installed_apps()

    def find_camera_package(self):
        """Find the actual camera package on this device"""
        try:
            camera_packages = [
                'com.android.camera',
                'com.android.camera2',
                'com.sec.android.app.camera',  
                'com.huawei.camera',           
                'com.sonyericsson.android.camera',  
                'com.oneplus.camera',          
                'com.motorola.camera',         
                'com.google.android.GoogleCamera'  
            ]
            
            for package in camera_packages:
                result = subprocess.run(f"adb shell pm list packages | grep {package}",
                                     shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    return result.stdout.split(":")[-1].strip()
            return None
        except Exception as e:
            print(f"Error finding camera package: {e}")
            return None

    def get_installed_apps(self):
        try:
            user_apps = subprocess.run("adb shell pm list packages -3",
                                     shell=True, capture_output=True, text=True)
            system_apps = subprocess.run("adb shell pm list packages -s",
                                       shell=True, capture_output=True, text=True)
            
            all_packages = []
            for output in [user_apps, system_apps]:
                packages = [line.split(":")[-1].strip() 
                          for line in output.stdout.split("\n") 
                          if line.strip()]
                all_packages.extend(packages)
            
            return list(set(all_packages))  
        except Exception as e:
            print(f"Error fetching installed apps: {e}")
            return []

    def correct_app_name(self, user_input):
        user_input = user_input.lower()
        
        if user_input in self.common_apps:
            package = self.common_apps[user_input]['package']
            if package in self.installed_apps:
                return package
        
        prompt = f"""Find the correct app package name.
        User input: '{user_input}'
        Installed packages: {self.installed_apps}
        Common mappings: {self.common_apps}
        
        Return ONLY the package name, nothing else.
        If unsure, return: UNKNOWN"""
        
        try:
            response = model.generate_content(prompt)
            package = response.text.strip()
            
            if package != "UNKNOWN" and package in self.installed_apps:
                return package
            
            matches = process.extractBests(user_input, self.installed_apps, score_cutoff=70, limit=3)
            if matches:
                return matches[0][0]  
                
        except Exception as e:
            print(f"Error in app name correction: {e}")
        
        return None

    def get_main_activity(self, package_name: str) -> str:
        try:
            commands = [
                f"adb shell dumpsys package {package_name} | grep -A 3 'android.intent.action.MAIN:'",
                f"adb shell cmd package resolve-activity --brief {package_name}",
                f"adb shell pm dump {package_name} | grep -A 1 'MAIN'",
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output = result.stdout.strip()
                
                if output:
                    matches = re.findall(rf'{package_name}/[.\w]+', output)
                    if matches:
                        activity = matches[0].split('/', 1)[1]
                        print(f"Found activity: {activity}")
                        return activity
            
            return None
        except Exception as e:
            print(f"Error finding main activity: {e}")
            return None

    def verify_app_launch(self, package_name: str, max_wait: int = 3) -> bool:
        print("Verifying app launch...")
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            try:
                result = subprocess.run(
                    "adb shell dumpsys window | grep -E 'mCurrentFocus'",
                    shell=True, capture_output=True, text=True
                )
                if package_name in result.stdout:
                    return True
                time.sleep(0.5)
            except Exception:
                pass
        return False

    def open_app(self, app_name: str) -> bool:
        app_name = app_name.lower()
        
        if app_name in self.common_apps:
            app_info = self.common_apps[app_name]
            package_name = app_info['package']
            main_activity = app_info['activity']
        else:
            package_name = self.correct_app_name(app_name)
            main_activity = None
        
        if not package_name:
            print(f"Could not find app: {app_name}")
            return False
            
        print(f"Attempting to launch {app_name} ({package_name})")
        
        try:
            if main_activity:
                cmd = f"adb shell am start -n {package_name}/{main_activity}"
                print(f"Trying direct launch: {cmd}")
                subprocess.run(cmd, shell=True)
                
                if self.verify_app_launch(package_name):
                    print("✓ App launched successfully on first attempt")
                    return True
            
            cmd = f"adb shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
            print(f"Trying package launch: {cmd}")
            subprocess.run(cmd, shell=True)
            
            if self.verify_app_launch(package_name):
                print("✓ App launched successfully with package launch")
                return True
                
        except Exception as e:
            print(f"Launch error: {e}")
        
        print("✗ Failed to launch app")
        return False
