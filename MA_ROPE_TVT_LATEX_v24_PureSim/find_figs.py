from PIL import Image
import numpy as np

img = Image.open('/tmp/page6-06.png').convert('L')
arr = np.array(img)

# Find horizontal lines that are mostly non-white to locate the image
row_means = arr.mean(axis=1)

# print rows that have significant non-white content
for i, m in enumerate(row_means):
    if m < 250:
        print(f"Content at row {i}")
        break

for i in range(len(row_means)-1, -1, -1):
    if row_means[i] < 250:
        print(f"Content ends at row {i}")
        break

