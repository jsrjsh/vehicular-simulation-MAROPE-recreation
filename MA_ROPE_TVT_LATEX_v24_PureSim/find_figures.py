from PIL import Image

def find_figure_in_col(im_col):
    im_col_gray = im_col.convert('L')
    pixels = im_col_gray.load()
    width, height = im_col_gray.size
    
    row_density = []
    for y in range(height):
        dark_pixels = 0
        for x in range(width):
            if pixels[x, y] < 200:
                dark_pixels += 1
        row_density.append(dark_pixels)
        
    blocks = []
    start = None
    for y, d in enumerate(row_density):
        if d > 10:
            if start is None:
                start = y
        else:
            if start is not None:
                blocks.append((start, y))
                start = None
    if start is not None:
        blocks.append((start, height))
        
    merged = []
    if not blocks: return None
    curr = list(blocks[0])
    for b in blocks[1:]:
        if b[0] - curr[1] < 40: # INCREASED MERGE THRESHOLD
            curr[1] = b[1]
        else:
            merged.append(curr)
            curr = list(b)
    merged.append(curr)
    
    print(f"Blocks > 100px:")
    for b in merged:
        if b[1]-b[0] > 100:
            print(f"  {b[0]} to {b[1]} (height={b[1]-b[0]})")
    
    largest_block = max(merged, key=lambda b: b[1]-b[0])
    return largest_block

im = Image.open('/tmp/page6_render-06.png')
w, h = im.size
mid = 1251

print("--- Left Column ---")
left = im.crop((150, 200, mid-50, h-200)) # crop margins
l_start, l_end = find_figure_in_col(left)

print("--- Right Column ---")
right = im.crop((mid+50, 200, w-150, h-200))
r_start, r_end = find_figure_in_col(right)

