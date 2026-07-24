import docx

def fix_issues(filepath):
    doc = docx.Document(filepath)
    modified = False

    # Issue 1: compute deadline explanation
    old_deadline = "15% compute (1000 ms in the compiled results)"
    new_deadline = "15% compute (evaluated at a stricter 1000 ms deadline in the experimental results)"

    # Issue 2: materially alter -> materially affect
    old_materially = "materially alter"
    new_materially = "materially affect"

    for p in doc.paragraphs:
        if old_deadline in p.text:
            p.text = p.text.replace(old_deadline, new_deadline)
            modified = True
        if old_materially in p.text:
            p.text = p.text.replace(old_materially, new_materially)
            modified = True

    if modified:
        doc.save(filepath)
        print("Fixes applied successfully.")
    else:
        print("No matches found or no changes needed.")

if __name__ == "__main__":
    fix_issues('MA_ROPE_IEEE_Paper_v21.docx')
