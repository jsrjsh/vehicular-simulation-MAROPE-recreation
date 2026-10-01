from PIL import Image
import numpy as np

img = Image.open('/tmp/page6-06.png')
# size is 1275 x 1650
# Let's crop out the margins.
# left margin ~ 100, right margin ~ 1175
# top margin ~ 150, bottom margin ~ 1500

# The page contains TWO subfigures. (a) and (b).
# Let's just crop the top half for (a) and bottom half for (b), excluding margins.

box_a = (100, 150, 1175, 750)
box_b = (100, 750, 1175, 1400)

img_a = img.crop(box_a)
img_b = img.crop(box_b)

img_a.save('figures/real_fig2a.png')
img_b.save('figures/real_fig2b.png')
print("Cropped successfully!")
