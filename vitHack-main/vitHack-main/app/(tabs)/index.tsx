import React, { useState, useEffect } from "react";
import { View, Text, Button, ActivityIndicator, StyleSheet } from "react-native";
import { WebView } from "react-native-webview";
import * as Speech from "expo-speech";

const SpeechApp = () => {
  const [spokenText, setSpokenText] = useState("");
  const [apiText, setApiText] = useState("");
  const [loading, setLoading] = useState(true);

  const html = `
  <html>
    <head>
      <style>
        body {
          font-family: 'Poppins', sans-serif;
          text-align: center;
          background: linear-gradient(135deg, #1e3c72, #2a5298, #6c5ce7);
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          height: 100vh;
          margin: 0;
          overflow: hidden;
        }

        h1 {
          color: #ffffff;
          font-size: 50px;
          font-weight: bold;
          text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
        }

        h2 {
          background: rgba(255, 255, 255, 0.15);
          color: #ffffff;
          font-size: 30px;
          padding: 12px 20px;
          border-radius: 12px;
          backdrop-filter: blur(10px);
          box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
          margin-bottom: 20px;
          transition: all 0.3s ease-in-out;
        }

        h2.listening {
          background: rgba(255, 255, 255, 0.3);
          color: #f1c40f;
          transform: scale(1.05);
        }

        p {
          font-size: 18px;
          color: #ddd;
          margin-top: 20px;
          padding: 10px 20px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
          backdrop-filter: blur(8px);
        }

        .microphone {
          display: none;
          margin-top: 20px;
          width: 150px;
          height: 150px;
          filter: drop-shadow(0px 4px 6px rgba(0, 0, 0, 0.3));
          transition: all 0.3s ease-in-out;
        }

        .listening .microphone {
          display: block;
          transform: scale(1.2);
        }

        .button {
          margin-top: 20px;
          padding: 12px 24px;
          font-size: 16px;
          font-weight: bold;
          color: #fff;
          background: linear-gradient(135deg, #ff9a9e, #fad0c4);
          border: none;
          border-radius: 8px;
          cursor: pointer;
          box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
          transition: transform 0.2s ease, box-shadow 0.3s ease;
        }

        .button:hover {
          transform: scale(1.05);
          box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.4);
        }
      </style>

    </head>
    <body>
      <h1>Voice-Activated Speech Recognition</h1>
      <h2 id="outputText">Say "Hey Sandy" to start recording.</h2>
      <svg id="micIcon" class="microphone" fill="#000000" height="200px" width="200px" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
        <g>
          <g>
            <path d="m439.5,236c0-11.3-9.1-20.4-20.4-20.4s-20.4,9.1-20.4,20.4c0,70-64,126.9-142.7,126.9-78.7,0-142.7-56.9-142.7-126.9 0-11.3-9.1-20.4-20.4-20.4s-20.4,9.1-20.4,20.4c0,86.2 71.5,157.4 163.1,166.7v57.5h-23.6c-11.3,0-20.4,9.1-20.4,20.4 0,11.3 9.1,20.4 20.4,20.4h88c11.3,0 20.4-9.1 20.4-20.4 0-11.3-9.1-20.4-20.4-20.4h-23.6v-57.5c91.6-9.3 163.1-80.5 163.1-166.7z"/>
            <path d="m256,323.5c51,0 92.3-41.3 92.3-92.3v-127.9c0-51-41.3-92.3-92.3-92.3s-92.3,41.3-92.3,92.3v127.9c0,51 41.3,92.3 92.3,92.3zm-52.3-220.2c0-28.8 23.5-52.3 52.3-52.3s52.3,23.5 52.3,52.3v127.9c0,28.8-23.5,52.3-52.3,52.3s-52.3-23.5-52.3-52.3v-127.9z"/>
          </g>
        </g>
      </svg>
      
      <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        let isListening = false;
        
        recognition.onresult = (event) => {
          const transcript = event.results[event.results.length - 1][0].transcript.trim();
          if (!isListening && transcript.toLowerCase() === 'hey sandy') {
            isListening = true;
            document.getElementById('outputText').innerText = "Listening...";
            document.getElementById('micIcon').style.display = "block";
          } else if (isListening) {
            window.ReactNativeWebView.postMessage(transcript);
            isListening = false;
            document.getElementById('outputText').innerText = 'Say "Hey Sandy" to start recording.';
            document.getElementById('micIcon').style.display = "none";
          }
        };

        recognition.onend = () => {
          recognition.start();
        };

        recognition.start();
      </script>
    </body>
  </html>
  `;

  useEffect(() => {
    const fetchText = async () => {
      try {
        const response = await fetch("http://172.16.45.67:5000/api/text");
        const data = await response.json();
        setApiText(data.message);
      } catch (error) {
        console.error("Error fetching text:", error);
        setApiText("Failed to fetch text.");
      } finally {
        setLoading(false);
      }
    };
    fetchText();
  }, []);

  const sendToBackend = async (text) => {
    try {
      const response = await fetch("http://172.16.45.67:5000/api/speech", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${errorText}`);
      }
      const data = await response.json();
      console.log("Backend response:", data);

      const textResponse = await fetch("http://172.16.45.67:5000/api/text");
      const textData = await textResponse.json();

      setApiText(textData.message);
      Speech.speak(textData.message, { language: "en-US", pitch: 1.2, rate: 1.0 });
    } catch (error) {
      console.error("Error sending to backend:", error);
    }
  };

  const speakApiText = () => {
    if (apiText) {
      Speech.speak(apiText, { language: "en-US", pitch: 1.2, rate: 1.0 });
    }
  };

  return (
    <View style={styles.container}>
      
      <View style={styles.webViewContainer}>
        <WebView
          originWhitelist={["*"]}
          source={{ html }}
          onMessage={(event) => {
            setSpokenText(event.nativeEvent.data);
            sendToBackend(event.nativeEvent.data);
          }}
          style={styles.webView}
        />
      </View>
      {/* <Text style={styles.recognizedText}>
        Recognized: {spokenText}
      </Text> */}

      
      {/* <View style={styles.apiMessageContainer}>
        {loading ? (
          <ActivityIndicator size="large" color="blue" />
        ) : (
          <>
            <Text style={styles.apiMessageText}>
              API Message: {apiText}
            </Text>
            <Button
              title="Speak API Message"
              onPress={speakApiText}
              color="#2196F3"
            />
          </>
        )}
      </View> */}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  webViewContainer: {
    flex: 1,
  },
  webView: {
    flex: 1,
  },
  recognizedText: {
    padding: 15,
    fontSize: 16,
    color: '#333',
  },
  apiMessageContainer: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#ccc',
    backgroundColor: '#fff',
  },
  apiMessageText: {
    fontSize: 14,
    marginBottom: 15,
    color: '#555',
  },
});

export default SpeechApp;
