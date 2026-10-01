from PIL import Image

def find_largest_block(im_col):
    im_col_gray = im_col.convert('L')
    pixels = im_col_gray.load()
    width, height = im_col_gray.size
    
    non_white_rows = []
    for y in range(height):
        row_is_white = True
        for x in range(width):
            if pixels[x, y] < 250:
                row_is_white = False
                break
        if not row_is_white:
            non_white_rows.append(y)
            
    blocks = []
    if non_white_rows:
        start = non_white_rows[0]
        last = non_white_rows[0]
        for y in non_white_rows[1:]:
            if y - last > 30: # smaller gap threshold
                blocks.append((start, last))
                start = y
            last = y
        blocks.append((start, last))
        
    largest_block = max(blocks, key=lambda b: b[1]-b[0])
    return largest_block

im = Image.open('/tmp/page6_render-06.png')
w, h = im.size
mid = 1251

# Left column
left = im.crop((0, 200, mid, h-200))
l_start, l_end = find_largest_block(left)
print(f"Left col largest block: y={l_start} to {l_end}, height={l_end-l_start}")
left_fig = left.crop((0, l_start, mid, l_end))
left_fig.save('figures/real_fig2a.png')

# Right column
right = im.crop((mid, 200, w, h-200))
r_start, r_end = find_largest_block(right)
print(f"Right col largest block: y={r_start} to {r_end}, height={r_end-r_start}")
right_fig = right.crop((0, r_start, w-mid, r_end))
right_fig.save('figures/real_fig2b.png')

