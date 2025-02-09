import React, { useEffect, useState } from "react";
import { View, Text, Button, Alert } from "react-native";
import * as Location from "expo-location";
import io from "socket.io-client";
import Tts from "react-native-tts";

const SERVER_URL = "http://192.168.29.251.:5000"; // Change to your Flask server IP
const socket = io(SERVER_URL);

export default function App() {
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [sessionId, setSessionId] = useState<string>("");

  useEffect(() => {
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission Denied", "Location access is required for navigation.");
        return;
      }

      let loc = await Location.getCurrentPositionAsync({});
      setLocation({ latitude: loc.coords.latitude, longitude: loc.coords.longitude });
    })();
  }, []);

  const startNavigation = async () => {
    const response = await fetch(`${SERVER_URL}/start-navigation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origin: "Central Park, NY", destination: "Times Square, NY" })
    });

    const data = await response.json();
    if (data.session_id) {
      setSessionId(data.session_id);
      startTracking();
    } else {
      Alert.alert("Error", "Failed to start navigation.");
    }
  };

  const startTracking = async () => {
    await Location.watchPositionAsync(
      { accuracy: Location.Accuracy.High, distanceInterval: 1 },
      (loc) => {
        setLocation({ latitude: loc.coords.latitude, longitude: loc.coords.longitude });
        socket.emit("location_update", {
          session_id: sessionId,
          lat: loc.coords.latitude,
          lng: loc.coords.longitude,
        });
      }
    );
  };

  useEffect(() => {
    const handleNavigationInstruction = (data: { instruction: string }) => {
      Alert.alert("Navigation", data.instruction);
      Tts.speak(data.instruction);
    };

    socket.on("navigation_instruction", handleNavigationInstruction);

    return () => {
      socket.off("navigation_instruction", handleNavigationInstruction);
    };
  }, []);

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Text>Live Location: {location?.latitude}, {location?.longitude}</Text>
      <Button title="Start Navigation" onPress={startNavigation} />
    </View>
  );
}
