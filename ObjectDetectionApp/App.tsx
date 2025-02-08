import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useState, useRef } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, Image } from 'react-native';
import axios from 'axios';
import { Audio } from 'expo-av';

export default function App() {
  const [facing, setFacing] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const cameraRef = useRef<any>(null);

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need your permission to use the camera</Text>
        <Button onPress={requestPermission} title="Grant Permission" />
      </View>
    );
  }
  const SERVER_URL = 'http://192.168.29.251:5000';
  async function captureAndSendImage() {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync({ base64: true });
      setCapturedImage(photo.uri); // Show captured image
      const base64Image = photo.base64;
     

      try {
        const response = await axios.post(`${SERVER_URL}/detect`, { image: base64Image });
        console.log(response.data);

        // If there is an audio alert, play it
        if (response.data.alert) {
          playAudioAlert();
        }
      } catch (error) {
        console.error("Error sending image:", error);
      }
    }
  }

  async function playAudioAlert() {
    try {
      const sound = new Audio.Sound();
      await sound.loadAsync({ uri: `${SERVER_URL}/alert.mp3` });
      await sound.playAsync();
    } catch (error) {
      console.error("Error playing audio:", error);
    }
  }

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={styles.camera} facing={facing} />
      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.button} onPress={captureAndSendImage}>
          <Text style={styles.text}>Capture & Detect</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={() => setFacing(facing === 'back' ? 'front' : 'back')}>
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
});
