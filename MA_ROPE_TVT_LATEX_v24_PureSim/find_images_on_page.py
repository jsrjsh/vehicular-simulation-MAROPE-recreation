import cv2
import numpy as np

# Load the page image
image = cv2.imread('/tmp/page6_render-06.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (51,51), 0)
thresh = cv2.threshold(blur, 240, 255, cv2.THRESH_BINARY_INV)[1]

# Find contours
cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

boxes = []
for c in cnts:
    x, y, w, h = cv2.boundingRect(c)
    if w > 500 and h > 500: # Filter small text blocks
        boxes.append((x, y, w, h))

# Sort boxes top to bottom
boxes.sort(key=lambda b: b[1])

print(f"Found {len(boxes)} large image regions.")
for i, (x, y, w, h) in enumerate(boxes):
    print(f"Region {i}: (x={x}, y={y}, w={w}, h={h})")
    crop = image[y:y+h, x:x+w]
    cv2.imwrite(f'/tmp/page6_crop_{i}.png', crop)
