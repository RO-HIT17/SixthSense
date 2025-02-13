# Sixth Sense

## Overview
Sixth Sense is an AI-powered **real-time assistant** designed to aid visually impaired individuals in **navigation, object detection, and automation of daily tasks**. Utilizing **computer vision, voice recognition, and conversational AI**, this system provides real-time feedback on the surrounding environment through **audio alerts** and enables seamless **voice-command-based interactions**.

## Key Features
- **Real-Time Object & Obstacle Detection**: Identifies objects and obstacles in the user's path and provides audio alerts with relative distance.
- **Indoor & Outdoor Navigation**: Provides voice-guided navigation from one location to another.
- **Conversational AI Interface**: Accepts and processes **voice commands** for various tasks.
- **Image, Face, and Text Recognition**: Describes specific images, recognizes faces, and extracts text.
- **Environmental Awareness**: Describes what’s happening around the user.
- **Smart Assistant Features**: Allows texting, calling, and other mobile interactions via voice commands.

## Technologies Used
- **Computer Vision**: OpenCV, YOLO (You Only Look Once) for object detection.
- **Speech Processing**: Azure Speech Services for voice commands and text-to-speech.
- **Cloud Services**: Azure Cognitive Services (Computer Vision, Speech APIs).
- **Automation & Device Control**: ADB (Android Debug Bridge) for mobile automation.

## Workflow
1. **User opens the mobile app** and provides a live camera feed.
2. The system **detects objects & obstacles** in real-time and alerts the user.
3. The user can **issue voice commands** to perform actions like navigation, object recognition, or automation tasks.
4. If a destination is provided, the app offers **step-by-step voice-guided navigation**.
5. The system integrates with third-party apps for tasks like calling, messaging, or media playback.

## Voice Command Actions
- **Navigation & Object Detection**:
  - Get directions (source & destination).
  - Detect obstacles in a path with relative distance.
  - Describe images or surroundings.
- **Text & Speech Processing**:
  - Extract text from an image.
  - Read out what’s on the screen.
- **App Integrations & Automation**:
  - Search on YouTube.
  - Search on Google.
  - Send a WhatsApp message.
  - Play music on Spotify.
  - Order food via Zomato.
  - Book a ride on Rapido.
  - Book tickets via Redbus.
  - Check unread messages on WhatsApp.
  - Upload an Instagram story.
  - Send a WhatsApp voice message.

## Installation & Setup
### **Prerequisites**
- Python 3.x
- OpenCV, YOLO, Azure SDKs
- Android Debug Bridge (ADB) for automation

### **Installation Steps**
1. **Clone the Repository**
   ```sh
   git clone https://github.com/RO-HIT17/SixthSense.git
   cd sixthsense
   ```
2. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set Up Azure Services**
   - Create an **Azure Cognitive Services** account.
   - Obtain **API keys** for **Speech** and **Computer Vision**.
   - Store them in an `.env` file:
     ```sh
     AZURE_SPEECH_KEY=your_speech_api_key
     AZURE_VISION_KEY=your_vision_api_key
     ```
4. **Enable ADB for Mobile Automation**
   ```sh
   adb tcpip 5555
   adb connect DEVICE_IP:5555
   ```
5. **Run the Application**
   ```sh
   python main.py
   ```

## Future Enhancements  

- **Offline Functionality**: Reduce dependency on cloud services for better accessibility and performance.  
- **Advanced NLP Integration**: Improve natural language processing to enhance conversational capabilities.  
- **Wearable Support**: Extend functionality to smart glasses and other assistive wearables.  
- **AI-Powered Assistance**: Evolve towards a Jarvis-like AI assistant for comprehensive automation.  
- **Enhanced Depth Estimation**: Improve object detection accuracy with advanced depth perception for safer navigation.  
- **Smart Device & App Integration**: Enable seamless interaction with IoT devices and third-party applications.  
- **Contextual Awareness**: Provide more personalized and situation-aware assistance for users.  
