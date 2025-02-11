import "react-native-get-random-values";
import React, { useState } from "react";
import { View, Button, Text, Alert, StyleSheet } from "react-native";
import { Audio, RecordingOptions } from "expo-av";
import * as FileSystem from "expo-file-system";

const API_URL = "http://172.16.44.247:5000/upload"; // Flask backend

const AudioRecorder: React.FC = () => {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState<string | null>(null);

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== "granted") {
        alert("Permission needed to record audio");
        return;
      }

      const newRecording = new Audio.Recording();
      await newRecording.prepareToRecordAsync({
        android: {
          extension: ".wav", // Save as WAV
          outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_MPEG_4,
          audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_AAC,
          sampleRate: 44100,
          numberOfChannels: 1,
          bitRate: 128000,
        },
        ios: {
          extension: ".wav",
          outputFormat: Audio.RECORDING_OPTION_IOS_OUTPUT_FORMAT_MPEG4AAC,
          audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_MAX,
          sampleRate: 44100,
          numberOfChannels: 1,
          bitRate: 128000,
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
        web: {
          mimeType: "audio/webm",
          bitsPerSecond: 128000,
        },
      } as RecordingOptions);

      await newRecording.startAsync();
      setRecording(newRecording);
      setIsRecording(true);
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  };

  const stopRecording = async () => {
    if (!recording) return;
    try {
      await recording.stopAndUnloadAsync();
      setIsRecording(false);

      const uri = recording.getURI();
      setRecording(null);

      if (uri) {
        await sendToBackend(uri);
      }
    } catch (error) {
      console.error("Error stopping recording:", error);
    }
  };

  const sendToBackend = async (uri: string) => {
    try {
      const fileInfo = await FileSystem.getInfoAsync(uri);
      if (!fileInfo.exists) {
        Alert.alert("Error", "Audio file not found!");
        return;
      }

      const fileData = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });

      const formData = new FormData();
      formData.append("file", {
        uri,
        name: "audio.wav",
        type: "audio/wav",
      } as any);

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "multipart/form-data",
        },
        body: formData,
      });

      const responseData = await response.json();
      setTranscription(responseData.transcription || "No transcription available.");
    } catch (error) {
      console.error("Error sending audio:", error);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.buttonContainer}>
        <Button
          title={isRecording ? "Stop Recording" : "Start Recording"}
          onPress={isRecording ? stopRecording : startRecording}
        />
      </View>
      {transcription && (
        <View style={styles.transcriptionContainer}>
          <Text style={styles.transcriptionText}>Transcription: {transcription}</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  buttonContainer: {
    width: "80%",
    marginBottom: 20,
  },
  transcriptionContainer: {
    width: "90%",
    padding: 15,
    backgroundColor: "#f5f5f5",
    borderRadius: 10,
    marginTop: 20,
  },
  transcriptionText: {
    fontSize: 16,
    textAlign: "center",
  },
});

export default AudioRecorder;
