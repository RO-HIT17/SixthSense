import cv2
import numpy as np
import pyttsx3

import time

yolo_net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]

with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

cap = cv2.VideoCapture(0)

while True:
    engine = pyttsx3.init()
    ret, frame = cap.read()
    height, width, channels = frame.shape

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

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            if class_ids[i] in [3, 6, 8]:  # car, bus, truck
                if confidence >= 0.5:
                    mid_x = (x + x + w) / 2
                    mid_y = (y + y + h) / 2
                    apx_distance = round(((1 - (h / height)) ** 4), 1)
                    cv2.putText(frame, '{}'.format(apx_distance), (int(mid_x * 800), int(mid_y * 450)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    if apx_distance <= 0.5:
                        if 0.3 < mid_x / width < 0.7:
                            cv2.putText(frame, 'WARNING!!!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                            print("Warning - Vehicles Approaching")
                            engine.say("Warning - Vehicles Approaching")

            if class_ids[i] == 40:  # bottle
                if confidence >= 0.5:
                    mid_x = (x + x + w) / 2
                    mid_y = (y + y + h) / 2
                    apx_distance = round(((1 - (h / height)) ** 4), 1)
                    cv2.putText(frame, '{}'.format(apx_distance), (int(mid_x * 800), int(mid_y * 450)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    print(apx_distance)
                    engine.say(apx_distance)
                    engine.say("units")
                    engine.say("BOTTLE IS AT A SAFER DISTANCE")

                    if apx_distance <= 0.5:
                        if 0.3 < mid_x / width < 0.7:
                            cv2.putText(frame, 'WARNING!!!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                            print("Warning - BOTTLE very close to the frame")
                            engine.say("Warning - BOTTLE very close to the frame")

            if class_ids[i] == 0:  # person
                print("Person Detected")
                if confidence >= 0.5:
                    mid_x = (x + x + w) / 2
                    mid_y = (y + y + h) / 2
                    apx_distance = round(((1 - (h / height)) ** 4), 1)
                    cv2.putText(frame, '{}'.format(apx_distance), (int(mid_x * 800), int(mid_y * 450)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    print(apx_distance)
                    engine.say(apx_distance)
                    #time.sleep(1)
                    engine.say("units")
                    engine.say("Person is AT A SAFER DISTANCE")

                    if apx_distance <= 0.5:
                        if 0.3 < mid_x / width < 0.7:
                            cv2.putText(frame, 'WARNING!!!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                            print("Warning - Person very close to the frame")
                            engine.say("Warning - Person very close to the frame")

        engine.runAndWait()
        if engine._inLoop:
            engine.endLoop()

    cv2.imshow("YOLO Object Detection", frame)
    cv2.waitKey(1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()