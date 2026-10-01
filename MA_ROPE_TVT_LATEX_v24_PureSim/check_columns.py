from PIL import Image

im = Image.open('/tmp/page6_render-06.png')
im = im.convert('L')
pixels = im.load()
width, height = im.size

# Check vertical columns for white gaps
white_cols = []
for x in range(width):
    col_is_white = True
    for y in range(240, 3123):
        if pixels[x, y] < 250:
            col_is_white = False
            break
    if col_is_white:
        white_cols.append(x)

if white_cols:
    print(f"Found {len(white_cols)} completely white vertical lines.")
    # Find middle gap
    middle = width // 2
    for x in white_cols:
        if abs(x - middle) < 200:
            print(f"Middle gap at x={x}")
else:
    print("No completely white vertical columns (maybe a figure* spans the width!)")

