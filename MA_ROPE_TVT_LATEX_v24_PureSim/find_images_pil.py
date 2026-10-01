from PIL import Image

im = Image.open('/tmp/page6_render-06.png')
# Convert to grayscale
im = im.convert('L')
pixels = im.load()
width, height = im.size

# Find all non-white rows
non_white_rows = []
for y in range(height):
    row_is_white = True
    for x in range(width):
        if pixels[x, y] < 250: # Threshold for white
            row_is_white = False
            break
    if not row_is_white:
        non_white_rows.append(y)

# Find blocks of non-white rows
blocks = []
if non_white_rows:
    start = non_white_rows[0]
    last = non_white_rows[0]
    for y in non_white_rows[1:]:
        if y - last > 50: # Gap of 50 pixels means new block
            blocks.append((start, last))
            start = y
        last = y
    blocks.append((start, last))

print(f"Found {len(blocks)} vertical blocks:")
for i, (start, end) in enumerate(blocks):
    h = end - start
    print(f"Block {i}: y={start} to {end} (height={h})")
    if h > 500:
        print(f"  Cropping large block {i}...")
        orig = Image.open('/tmp/page6_render-06.png')
        crop = orig.crop((0, start, width, end))
        crop.save(f'/tmp/page6_crop_{i}.png')

