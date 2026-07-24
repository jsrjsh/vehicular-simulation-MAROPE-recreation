# scripts/extract_docx.py
import zipfile
import xml.etree.ElementTree as ET

def docx_to_txt(docx_path, txt_path):
    try:
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # Word XML namespaces
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            paragraphs = []
            for p in root.findall('.//w:p', ns):
                texts = []
                for t in p.findall('.//w:t', ns):
                    if t.text:
                        texts.append(t.text)
                if texts:
                    paragraphs.append(''.join(texts))
                    
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(paragraphs))
            print(f"Successfully extracted document text to {txt_path}")
    except Exception as e:
        print(f"Error extracting text: {e}")

if __name__ == "__main__":
    docx_to_txt('/var/tmp/marope/MA_ROPE_IEEE_Paper_v10_final2.docx', 'scripts/extracted_paper_text.txt')
