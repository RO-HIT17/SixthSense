import React, { useEffect, useState } from "react";
import { View, Button, Alert } from "react-native";
import MapView, { Marker, Polyline } from "react-native-maps";
import MapViewDirections from "react-native-maps-directions";
import * as Location from "expo-location";
import * as Speech from "expo-speech";
import axios from "axios";

const GOOGLE_MAPS_APIKEY = "AIzaSyCqp2pupWd721YQPS1z2bPzVmD_F9vtiNs";

interface LocationCoords {
  latitude: number;
  longitude: number;
}

export default function MapsScreen() {
  const [location, setLocation] = useState<LocationCoords | null>(null);
  const [destination, setDestination] = useState<LocationCoords>({
    latitude: 37.7749, // Example: San Francisco
    longitude: -122.4194,
  });
  const [routeCoords, setRouteCoords] = useState<LocationCoords[]>([]);

  useEffect(() => {
    getLocation();
  }, []);

  async function getLocation() {
    let { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("Permission to access location was denied");
      return;
    }

    let currentLocation = await Location.getCurrentPositionAsync({});
    setLocation(currentLocation.coords);
  }

  async function fetchDirections() {
    if (!location) return;
    
    try {
      const response = await axios.get(
        `https://maps.googleapis.com/maps/api/directions/json?origin=${location.latitude},${location.longitude}&destination=${destination.latitude},${destination.longitude}&key=${GOOGLE_MAPS_APIKEY}`
      );

      const points = decodePolyline(response.data.routes[0].overview_polyline.points);
      setRouteCoords(points);

      const firstInstruction = response.data.routes[0].legs[0].steps[0].html_instructions;
      Speech.speak(`Start navigation. ${stripHTML(firstInstruction)}`);
    } catch (error) {
      console.error("Error fetching directions:", error);
    }
  }

  function stripHTML(html: string): string {
    return html.replace(/<[^>]+>/g, "");
  }

  return (
    <View style={{ flex: 1 }}>
      <MapView
        style={{ flex: 1 }}
        initialRegion={{
          latitude: location?.latitude || 37.7749,
          longitude: location?.longitude || -122.4194,
          latitudeDelta: 0.01,
          longitudeDelta: 0.01,
        }}
        showsUserLocation={true}
      >
        {location && <Marker coordinate={location} title="You are here" />}
        <Marker coordinate={destination} title="Destination" />
        {routeCoords.length > 0 && (
          <Polyline coordinates={routeCoords} strokeWidth={4} strokeColor="blue" />
        )}
      </MapView>

      <Button title="Start Navigation" onPress={fetchDirections} />
    </View>
  );
}

function decodePolyline(encoded: string): LocationCoords[] {
  let points: LocationCoords[] = [];
  let index = 0, lat = 0, lng = 0;

  while (index < encoded.length) {
    let b, shift = 0, result = 0;
    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    let dlat = ((result & 1) ? ~(result >> 1) : (result >> 1));
    lat += dlat;

    shift = 0;
    result = 0;
    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    let dlng = ((result & 1) ? ~(result >> 1) : (result >> 1));
    lng += dlng;

    points.push({ latitude: lat / 1e5, longitude: lng / 1e5 });
  }
  return points;
}
