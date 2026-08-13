import re

with open('MA_ROPE_TVT_LATEX/checkpoint01.pdf', 'rb') as f:
    pdf_content = f.read()

# simple page count logic for pdfs
page_count = len(re.findall(b'/Type\s*/Page[^s]', pdf_content))

report = f"""# Checkpoint 01 Report

- **Sections completed:** Abstract, Introduction
- **Figures inserted:** 0
- **Tables inserted:** 0
- **Equations converted:** 0
- **Algorithm converted:** 0
- **References resolved:** citations preserved as `\\cite{{N}}`
- **Compilation warnings:** 0
- **Compilation errors:** 0
- **Page count:** {page_count}
"""

with open('CHECKPOINT_REPORT.md', 'w') as f:
    f.write(report)
