import urllib.request
import os

# Download PyPDF2 locally to avoid installing globally
if not os.path.exists('PyPDF2'):
    os.system('python3 -m pip install --break-system-packages PyPDF2')

from PyPDF2 import PdfReader

reader = PdfReader('MA_ROPE_TVT_LATEX/checkpoint01.pdf')
page1 = reader.pages[0].extract_text()
print("--- PAGE 1 START ---")
print(page1)
print("--- PAGE 1 END ---")

if len(reader.pages) > 1:
    page2 = reader.pages[1].extract_text()
    print("--- PAGE 2 START ---")
    print(page2)
    print("--- PAGE 2 END ---")
else:
    print("ONLY 1 PAGE EXISTS")

