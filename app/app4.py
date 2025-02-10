import cv2

# Open webcam (scrcpy mirrors mobile camera to default webcam)
cap = cv2.VideoCapture(0)  

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Show the video feed
    cv2.imshow("Mobile Camera Feed", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
