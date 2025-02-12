import torch
import cv2
import numpy as np
from torchvision import transforms
from timm.models.vision_transformer import vit_base_patch16_224

model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
model.eval()

def preprocess(img):
    transform = transforms.Compose([
        transforms.Resize((384, 384)),
        transforms.ToTensor()
    ])
    return transform(img).unsqueeze(0)

def estimate_depth(image):
    input_img = preprocess(image)
    with torch.no_grad():
        depth_map = model(input_img)
    return depth_map.squeeze().numpy()

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    depth = estimate_depth(frame)
    cv2.imshow("Depth Map", depth)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
