from PIL import Image, ImageStat
img = Image.open('figures/real_fig2a.png')
extrema = img.getextrema()
print(extrema)
