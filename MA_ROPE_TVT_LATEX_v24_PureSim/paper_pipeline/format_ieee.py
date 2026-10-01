"""
format_ieee.py (v26 rebuild)

Applies an IEEE Transactions-style formatting pass to the pandoc-generated
base.docx: Times New Roman 10pt body, two-column section layout, numbered
headings (I./A./B. style), Index Terms/Acknowledgment styling, table/image
width capping so nothing overflows the column.

Run after preprocess_for_pandoc.py + pandoc conversion.
"""
import os
import docx
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

IN_PATH = "base.docx"
OUT_PATH = "MA_ROPE_IEEE_Paper_v32.docx"

BODY_FONT = "Times New Roman"
BODY_SIZE = Pt(10)
HEADING_COLOR = RGBColor(0, 0, 0)


def set_run_font(run, size=BODY_SIZE, bold=None, italic=None, name=BODY_FONT, color=HEADING_COLOR):
    run.font.name = name
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:cs"), name)
    run.font.size = size
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color


def two_column_section(section):
    sectPr = section._sectPr
    cols = sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        sectPr.append(cols)
    cols.set(qn("w:num"), "2")
    cols.set(qn("w:space"), "432")  # 0.3in gutter


def set_margins(section):
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(0.625)
    section.right_margin = Inches(0.625)


TOP_SECTIONS = [
    "Introduction", "Related Work", "System Model and Problem Formulation",
    "MA-ROPE: Algorithm Design", "Experiments and Results", "Conclusion",
]


def main():
    doc = docx.Document(IN_PATH)

    section = doc.sections[0]
    set_margins(section)
    two_column_section(section)

    section_counter = 0
    subsection_counter = 0

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue

        style_name = p.style.name if p.style else ""

        is_title = (text.startswith("MA-ROPE: Multi-RAT"))
        is_author = (text == "Anonymous Authors")
        is_abstract = text.startswith("Abstract—") or text.startswith("Abstract--")
        is_index_terms = text.startswith("Index Terms—") or text.startswith("Index Terms--")
        is_h1 = style_name.startswith("Heading 1") or (
            text in TOP_SECTIONS and style_name.startswith("Heading")
        )
        is_h2 = style_name.startswith("Heading 2")
        is_refs_header = (text == "References")

        if is_title:
            for run in p.runs:
                set_run_font(run, size=Pt(18), bold=True)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue

        if is_author:
            for run in p.runs:
                set_run_font(run, size=Pt(11))
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue

        if is_abstract or is_index_terms:
            for run in p.runs:
                set_run_font(run, size=BODY_SIZE, italic=False)
            # Bold just the "Abstract—"/"Index Terms—" lead-in, matching
            # IEEEtran convention, by re-splitting the first run if needed.
            if p.runs:
                lead = "Abstract—" if is_abstract else "Index Terms—"
                if p.runs[0].text.startswith(lead):
                    p.runs[0].bold = True
                    p.runs[0].italic = True
            continue

        if is_refs_header:
            for run in p.runs:
                set_run_font(run, size=Pt(11), bold=True)
            # References is conventionally unnumbered in IEEE style and is
            # printed without a roman numeral below -- do NOT increment
            # section_counter here, or the Acknowledgment section (numbered
            # after References in document order) silently skips a number
            # (e.g. prints "VIII." right after "VI. CONCLUSION").
            subsection_counter = 0
            p.text = ""
            r = p.add_run("References")
            set_run_font(r, size=Pt(11), bold=True)
            continue

        if is_h1:
            section_counter += 1
            subsection_counter = 0
            roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"][section_counter - 1]
            new_text = f"{roman}. {text.upper()}"
            for run in list(p.runs):
                run.text = ""
            if p.runs:
                p.runs[0].text = new_text
                set_run_font(p.runs[0], size=Pt(11), bold=True)
            else:
                r = p.add_run(new_text)
                set_run_font(r, size=Pt(11), bold=True)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            continue

        if is_h2:
            subsection_counter += 1
            letter = chr(ord("A") + subsection_counter - 1)
            new_text = f"{letter}. {text}"
            for run in list(p.runs):
                run.text = ""
            if p.runs:
                p.runs[0].text = new_text
                set_run_font(p.runs[0], size=Pt(10), bold=True, italic=True)
            else:
                r = p.add_run(new_text)
                set_run_font(r, size=Pt(10), bold=True, italic=True)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            continue

        # Body text (incl. bold-italic pseudo-headers like "A. Task Offloading...",
        # captions, and everything else): normalize font/size/color, preserve
        # any existing bold/italic run formatting.
        for run in p.runs:
            set_run_font(run, size=BODY_SIZE, color=HEADING_COLOR)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.first_line_indent = None

        # Captions immediately preceding a continuous section break (wide
        # tables/figures) can render with stretched inter-word spacing in
        # LibreOffice, as if force-justified on their last line. Pin
        # left-alignment explicitly so this can't happen regardless of
        # section-break adjacency.
        if "Caption" in style_name:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Table styling: font size 8pt, column widths proportional to a fixed
    # total (not a flat per-cell width -- that overflowed badly for any
    # table with more than ~4 columns, since N columns x 3.3in each blew
    # straight through the single-column width and into the margin).
    SINGLE_COL_WIDTH = Inches(3.2)
    FULL_PAGE_WIDTH = Inches(7.15)  # 8.5in page - 0.625in x2 margins
    WIDE_TABLE_COLS = 4  # tables with this many columns or more go full-width

    def make_section_break(paragraph, num_cols):
        """Inserts a continuous section break at this paragraph, switching
        the column count for everything from here until the next break."""
        sectPr = OxmlElement("w:sectPr")
        cols = OxmlElement("w:cols")
        cols.set(qn("w:num"), str(num_cols))
        if num_cols == 2:
            cols.set(qn("w:space"), "432")
        sectPr.append(cols)
        sect_type = OxmlElement("w:type")
        sect_type.set(qn("w:val"), "continuous")
        sectPr.append(sect_type)
        pPr = paragraph._p.get_or_add_pPr()
        pPr.append(sectPr)

    def looks_numeric(text):
        text = text.strip()
        if not text:
            return False
        return text[0] in "0123456789+-~$"

    for t in doc.tables:
        n_cols = len(t.columns)
        for row_idx, row in enumerate(t.rows):
            for col_idx, cell in enumerate(row.cells):
                for cp in cell.paragraphs:
                    for run in cp.runs:
                        set_run_font(run, size=Pt(8))
                # Right-align numeric-looking data cells (not the header
                # row, not the leftmost label column) so decimal points
                # line up instead of ragged left-justified digit strings.
                if row_idx > 0 and col_idx > 0 and looks_numeric(cell.text):
                    for cp in cell.paragraphs:
                        cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        t.autofit = False

        if n_cols >= WIDE_TABLE_COLS:
            # A paragraph's sectPr describes the section ENDING at that
            # paragraph (OOXML semantics -- properties apply backward, not
            # forward). So: before_p ends the ongoing 2-col section (its
            # sectPr says num_cols=2); the table then lives in a new section
            # that isn't 1-column until after_p, placed right after the
            # table, whose sectPr says num_cols=1 to close that section out;
            # normal 2-col flow resumes automatically afterward from the
            # next section marker (or the body's trailing sectPr).
            tbl_elem = t._tbl
            # If a caption paragraph directly precedes the table, widen the
            # section starting there too -- otherwise the caption is left
            # in the outgoing 2-column section and LibreOffice mis-renders
            # its single line with a large stretched gap at the section
            # boundary. bookmarkStart/End markers (\label{}) can sit between
            # the caption and the table; skip past those to find it.
            anchor_before = tbl_elem
            prev_elem = tbl_elem.getprevious()
            while prev_elem is not None and prev_elem.tag != qn("w:p"):
                prev_elem = prev_elem.getprevious()
            if prev_elem is not None:
                pStyle = prev_elem.find(".//" + qn("w:pStyle"))
                if pStyle is not None and "Caption" in (pStyle.get(qn("w:val")) or ""):
                    anchor_before = prev_elem
            before_p = OxmlElement("w:p")
            anchor_before.addprevious(before_p)
            before_para = docx.text.paragraph.Paragraph(before_p, t._parent)
            make_section_break(before_para, 2)

            col_w = int(FULL_PAGE_WIDTH / n_cols)
            for row in t.rows:
                for cell in row.cells:
                    cell.width = col_w

            after_p = OxmlElement("w:p")
            tbl_elem.addnext(after_p)
            after_para = docx.text.paragraph.Paragraph(after_p, t._parent)
            make_section_break(after_para, 1)
        else:
            col_w = int(SINGLE_COL_WIDTH / max(n_cols, 1))
            for row in t.rows:
                for cell in row.cells:
                    cell.width = col_w

    # Image width: single-column cap (~3.4in) by default; wide composite
    # figures instead get the full-page-width treatment, via the same
    # section-break technique used for wide tables above. Pandoc renames
    # embedded media (image5_6_combined.png -> imageN.png), so filenames
    # can't identify them by the time format_ieee.py runs the resulting
    # docx; native pixel width is used instead (wide composites are
    # noticeably wider than any single-panel figure in this document).
    def native_pixel_width(inline_elem):
        blip = inline_elem.find(".//" + qn("a:blip"))
        if blip is None:
            return None
        rId = blip.get(qn("r:embed"))
        if rId is None or rId not in doc.part.rels:
            return None
        part = doc.part.rels[rId].target_part
        try:
            from io import BytesIO
            from PIL import Image as PILImage
            with PILImage.open(BytesIO(part.blob)) as im:
                return im.width
        except Exception:
            return None

    WIDE_FIGURE_PX_THRESHOLD = 1800

    def set_keep_next(paragraph):
        # Prevents Word/LibreOffice from splitting a figure from its
        # caption across a column break -- without this, an image that
        # lands near the bottom of a column can push its caption alone
        # into the top of the next column.
        pPr = paragraph._p.get_or_add_pPr()
        if pPr.find(qn("w:keepNext")) is None:
            pPr.append(OxmlElement("w:keepNext"))

    def starts_new_section(paragraph_elem):
        # True if the nearest preceding paragraph (skipping non-paragraph
        # siblings like bookmarkStart/End, which sit between a wide table's
        # closing section-break marker and the next real content) is a bare
        # section-break marker -- i.e. this paragraph is the first content
        # of a freshly opened section, most often right after a wide
        # table's closing break.
        prev_elem = paragraph_elem.getprevious()
        while prev_elem is not None and prev_elem.tag != qn("w:p"):
            prev_elem = prev_elem.getprevious()
        if prev_elem is None:
            return False
        pPr = prev_elem.find(qn("w:pPr"))
        return pPr is not None and pPr.find(qn("w:sectPr")) is not None

    for p in doc.paragraphs:
        drawings = p._p.findall(".//" + qn("w:drawing"))
        for drawing in drawings:
            inline_elem = drawing.find(qn("wp:inline"))
            if inline_elem is None:
                continue
            # keepNext right after a section-break marker makes LibreOffice
            # blank out the rest of the page instead of just pushing this
            # one figure down (observed on Table 1 -> Fig 1 and Table 6 ->
            # the merged Fig 5/6 figure); skip ONLY keepNext in that case --
            # sizing below must still run for every image regardless.
            if not starts_new_section(p._p):
                set_keep_next(p)
                next_elem = p._p.getnext()
                if next_elem is not None and next_elem.tag == qn("w:p"):
                    set_keep_next(docx.text.paragraph.Paragraph(next_elem, p._parent))
            px_w = native_pixel_width(inline_elem)
            extent = inline_elem.find(qn("wp:extent"))
            if extent is None:
                continue
            cx = int(extent.get("cx"))
            cy = int(extent.get("cy"))
            if px_w is not None and px_w > WIDE_FIGURE_PX_THRESHOLD:
                new_cx = FULL_PAGE_WIDTH
                new_cy = int(cy * (FULL_PAGE_WIDTH / cx))
                extent.set("cx", str(new_cx))
                extent.set("cy", str(new_cy))
                ext_elem = inline_elem.find(".//" + qn("a:ext"))
                if ext_elem is not None:
                    ext_elem.set("cx", str(new_cx))
                    ext_elem.set("cy", str(new_cy))
                before_p = OxmlElement("w:p")
                p._p.addprevious(before_p)
                before_para = docx.text.paragraph.Paragraph(before_p, p._parent)
                make_section_break(before_para, 2)
                # Widen the caption paragraph too, so it isn't narrow text
                # under a full-width figure: the section-closing break goes
                # after the NEXT paragraph (the caption) rather than right
                # after the image, if a caption paragraph follows.
                anchor_elem = p._p
                caption_elem = anchor_elem.getnext()
                if caption_elem is not None and caption_elem.tag == qn("w:p"):
                    anchor_elem = caption_elem
                after_p = OxmlElement("w:p")
                anchor_elem.addnext(after_p)
                after_para = docx.text.paragraph.Paragraph(after_p, p._parent)
                make_section_break(after_para, 1)
            else:
                # Normalize EVERY regular figure to exactly 3.4in width
                # (not just shrink oversized ones) -- pandoc assigns
                # different default embed sizes depending on the source
                # \includegraphics width attribute (e.g. 0.45\textwidth
                # figures embed ~30% smaller than \columnwidth figures),
                # so leaving undersized images alone produced a visibly
                # inconsistent figure scale across the document.
                ratio = Inches(3.4) / cx
                new_cx = Inches(3.4)
                new_cy = int(cy * ratio)
                extent.set("cx", str(new_cx))
                extent.set("cy", str(new_cy))
                ext_elem = inline_elem.find(".//" + qn("a:ext"))
                if ext_elem is not None:
                    ext_elem.set("cx", str(new_cx))
                    ext_elem.set("cy", str(new_cy))

    # Acknowledgment section with AI-disclosure text, appended before References.
    # Anchor on the References paragraph's own XML element (not a list index --
    # doc.paragraphs is recomputed from the tree on each access, so a second
    # index lookup after the first insertion would silently resolve to a
    # different paragraph and reverse the heading/body order).
    refs_anchor = None
    for p in doc.paragraphs:
        if p.text.strip() == "References":
            refs_anchor = p
            break

    if refs_anchor is not None:
        # refs_anchor is a stable reference to one fixed XML element, so two
        # insert_paragraph_before calls against it (not a re-looked-up list
        # index, which shifts after each insert) correctly stack in call
        # order: ack_para, then body_para, then refs_anchor.
        ack_para = refs_anchor.insert_paragraph_before("")
        body_para = refs_anchor.insert_paragraph_before("")

        section_counter += 1
        roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"][section_counter - 1]
        r = ack_para.add_run(f"{roman}. ACKNOWLEDGMENT")
        set_run_font(r, size=Pt(11), bold=True)
        ack_para.paragraph_format.space_before = Pt(10)
        ack_para.paragraph_format.space_after = Pt(4)

        ai_text = (
            "Claude (Anthropic) was used as an AI-assisted tool during portions of code "
            "development, data analysis, and manuscript preparation. All experimental "
            "results and scientific conclusions were independently reviewed and verified "
            "by the authors, who take full responsibility for the content."
        )
        r = body_para.add_run(ai_text)
        set_run_font(r, size=BODY_SIZE)
        body_para.paragraph_format.space_after = Pt(6)

    doc.save(OUT_PATH)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
