import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision import models

yolo_net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i-1] for i in yolo_net.getUnconnectedOutLayers()]

with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")  
midas.eval()

midas_transform = transforms.Compose([
    transforms.Resize((256, 256)),  
    transforms.ToTensor(),  
    transforms.Normalize(mean=[0.5], std=[0.5])  
])

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape
    midas_input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    midas_input = midas_transform(midas_input).unsqueeze(0)

    with torch.no_grad():
        depth_map = midas(midas_input)
    
    depth_map = depth_map.squeeze().cpu().numpy()
    depth_map = cv2.resize(depth_map, (width, height))
    depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())  

    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    yolo_net.setInput(blob)
    outs = yolo_net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4)

    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            color = (0, 255, 0)

            object_depth = np.mean(depth_map[y:y+h, x:x+w])  

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(frame, f"Depth: {object_depth:.2f} (normalized)", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("YOLO + AI Depth Estimation", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
