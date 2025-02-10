import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useState, useEffect, useRef } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, Image } from 'react-native';
import { io } from 'socket.io-client';
import { Audio } from 'expo-av';

export default function App() {
  const [facing, setFacing] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [camera, setCamera] = useState<any>(null); // Store CameraView instance
  const socketRef = useRef<any>(null);

  useEffect(() => {
    socketRef.current = io('http://192.168.29.251:5000', {
      transports: ['websocket'], // Use websocket transport explicitly
      reconnectionAttempts: 5, // Retry connection
      timeout: 5000,
    });

    socketRef.current.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
    });

    socketRef.current.on('detection_response', (data: any) => {
      console.log('Received detection:', data);
      if (data.success && data.objects?.length > 0) {
        playAudioAlert();
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

    if (camera) {
      try {
        const photo = await camera.takePictureAsync({ 
          base64: true,
          quality: 0.5  
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

  async function playAudioAlert() {
    try {
      const sound = new Audio.Sound();
      await sound.loadAsync({ uri: 'http://192.168.29.251:5000/alert.mp3' });
      await sound.playAsync();
    } catch (error) {
      console.error("Error playing audio:", error);
    }
  }

  return (
    <View style={styles.container}>
      <CameraView ref={(ref) => setCamera(ref)} style={styles.camera} facing={facing} />
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
  buttonDisabled: { backgroundColor: 'grey' }
});
