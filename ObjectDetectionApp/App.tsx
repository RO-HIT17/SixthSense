import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useState, useRef, useEffect } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, Image } from 'react-native';
import { io } from 'socket.io-client';
import { Audio } from 'expo-av';

export default function App() {
  const [facing, setFacing] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const cameraRef = useRef<any>(null);
  const socketRef = useRef<any>(null);

  useEffect(() => {
    // Initialize socket connection
    socketRef.current = io('http://172.16.44.247:5000');

    socketRef.current.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
    });

    socketRef.current.on('detection_response', async (data: any) => {
      console.log('Detection result:', data);
      setLoading(false);

      if (data.success && data.result.audio_url) {
        const audioUrl = `http://172.16.44.247:5000${data.result.audio_url}`;
        console.log('Playing audio from:', audioUrl);
        await playAudio(audioUrl);
      }
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need your permission to use the camera</Text>
        <Button onPress={requestPermission} title="Grant Permission" />
      </View>
    );
  }

  async function captureAndSendImage() {
    if (!connected) {
      console.log('Not connected to server');
      return;
    }

    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({ 
          base64: true,
          quality: 0.5  // Reduce image quality for faster transmission
        });
        setCapturedImage(photo.uri);

        // Send only the base64 data
        socketRef.current.emit('send_frame', {
          image: photo.base64
        });
      } catch (error) {
        console.error("Error capturing/sending image:", error);
      }
    }
  }

  async function playAudio(url: string) {
    try {
      const sound = new Audio.Sound();
      await sound.loadAsync({ uri: url });
      const result = await sound.playAsync();
      console.log('Audio playback started:', result);
      
      // Cleanup after playback
      sound.setOnPlaybackStatusUpdate(async (status) => {
        if (status.isLoaded && status.didJustFinish) {
          await sound.unloadAsync();
        }
      });
    } catch (error) {
      console.error("Error playing audio:", error);
    }
  }

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={styles.camera} facing={facing} />
      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={[styles.button, !connected && styles.buttonDisabled]} 
          onPress={captureAndSendImage}
          disabled={!connected}
        >
          <Text style={styles.text}>
            {connected ? 'Capture & Detect' : 'Connecting...'}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.button} 
          onPress={() => setFacing(facing === 'back' ? 'front' : 'back')}
        >
          <Text style={styles.text}>Flip Camera</Text>
        </TouchableOpacity>
      </View>
      {capturedImage && <Image source={{ uri: capturedImage }} style={styles.preview} />}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center' },
  camera: { flex: 1 },
  buttonContainer: { flexDirection: 'row', justifyContent: 'center', padding: 20 },
  button: { backgroundColor: 'blue', padding: 10, margin: 10, borderRadius: 5 },
  text: { color: 'white', fontWeight: 'bold' },
  preview: { width: 200, height: 200, alignSelf: 'center', marginTop: 20 },
  message: { textAlign: 'center', margin: 20, fontSize: 18, color: 'red' },
  buttonDisabled: {
    backgroundColor: 'grey',
    }
});