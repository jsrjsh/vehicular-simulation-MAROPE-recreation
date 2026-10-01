import re, glob

for f in glob.glob('sections/*.tex'):
    with open(f, 'r') as file:
        content = file.read()
    
    # Add a tiny vspace before subsections to disrupt pdftotext alignment issues
    # But wait, to fix C and D being flipped, let's just use \clearpage before sections if needed.
    pass

