import React, { useState, useEffect, useRef } from "react";
import { View, Button, Text } from "react-native";
import { CameraView, useCameraPermissions, CameraType } from "expo-camera";
import { io } from "socket.io-client";

export default function LiveStream() {
  const cameraRef = useRef<any>(null);
  const [facing, setFacing] = useState<CameraType>("back");
  const [permission, requestPermission] = useCameraPermissions();
  const [socket, setSocket] = useState<any>(null);
  const [detectedObjects, setDetectedObjects] = useState<string[]>([]);

  useEffect(() => {
    const newSocket = io("http://192.168.29.251:5000", { transports: ["websocket"] });
    setSocket(newSocket);
  
    newSocket.on("connect", () => {
      console.log("✅ Connected to WebSocket Server!");
    });
  
    newSocket.on("connect_error", (err) => {
      console.error("❌ WebSocket Connection Failed:", err);
    });
  
    newSocket.on("response", (data) => {
      console.log("📩 Received Response:", data);
      setDetectedObjects(data.objects);
    });
  
    return () => {
      newSocket.disconnect();
    };
  }, []);
  

  async function startStreaming() {
    if (!cameraRef.current) return;

    setInterval(async () => {
      const photo = await cameraRef.current.takePictureAsync({ base64: true });

      if (socket) {
        socket.emit("send_frame", { image: photo.base64 });
      }
    }, 500); // Send frame every 100ms
  }

  return (
    <View style={{ flex: 1 }}>
      {permission?.granted ? (
        <>
          <CameraView ref={cameraRef} facing={facing} style={{ height: 500 }} />
          <Button title="Start Streaming" onPress={startStreaming} />
          <Text>Detected Objects: {detectedObjects.join(", ")}</Text>
        </>
      ) : (
        <Button title="Grant Camera Permission" onPress={requestPermission} />
      )}
    </View>
  );
}
