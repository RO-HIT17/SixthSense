import base64

with open("test_image.jpeg", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
with open("s.txt","w") as f:
    f.write(base64_image)

print(base64_image)  # Copy this output
