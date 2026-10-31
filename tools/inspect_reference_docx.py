from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.oxml.ns import qn


REFERENCE = Path(r"C:\Users\gladk\Documents\MIREA\sem5\frameworks\Практическая работа 1 Гладких Иван ЭФБО-15-24.docx")
OUT = Path(r"C:\Users\gladk\Documents\MIREA\sem5\frameworks\personal_project\reports\template_qa\reference_evidence.json")


def emu(value):
    if value is None:
        return None
    return {"emu": int(value), "cm": round(value.cm, 3), "pt": round(value.pt, 3)}


def color(font):
    try:
        return str(font.color.rgb) if font.color.rgb else None
    except Exception:
        return None


def run_info(run):
    rpr = run._element.rPr
    rfonts = rpr.rFonts if rpr is not None else None
    return {
        "text": run.text,
        "bold": run.bold,
        "italic": run.italic,
        "underline": bool(run.underline) if run.underline is not None else None,
        "font_name": run.font.name,
        "font_size_pt": run.font.size.pt if run.font.size else None,
        "color": color(run.font),
        "ascii_font": rfonts.get(qn("w:ascii")) if rfonts is not None else None,
        "hansi_font": rfonts.get(qn("w:hAnsi")) if rfonts is not None else None,
    }


def paragraph_info(p, index, container="body"):
    pf = p.paragraph_format
    return {
        "container": container,
        "index": index,
        "style": p.style.name if p.style else None,
        "text": p.text,
        "alignment": str(p.alignment),
        "left_indent": emu(pf.left_indent),
        "right_indent": emu(pf.right_indent),
        "first_line_indent": emu(pf.first_line_indent),
        "space_before": emu(pf.space_before),
        "space_after": emu(pf.space_after),
        "line_spacing": str(pf.line_spacing),
        "keep_with_next": pf.keep_with_next,
        "keep_together": pf.keep_together,
        "page_break_before": pf.page_break_before,
        "runs": [run_info(r) for r in p.runs],
    }


def style_info(style):
    pf = style.paragraph_format
    f = style.font
    return {
        "name": style.name,
        "type": str(style.type),
        "base_style": style.base_style.name if style.base_style else None,
        "font_name": f.name,
        "font_size_pt": f.size.pt if f.size else None,
        "bold": f.bold,
        "italic": f.italic,
        "color": color(f),
        "alignment": str(pf.alignment),
        "left_indent": emu(pf.left_indent),
        "right_indent": emu(pf.right_indent),
        "first_line_indent": emu(pf.first_line_indent),
        "space_before": emu(pf.space_before),
        "space_after": emu(pf.space_after),
        "line_spacing": str(pf.line_spacing),
        "keep_with_next": pf.keep_with_next,
    }


doc = Document(REFERENCE)
data = {
    "reference": str(REFERENCE),
    "sha256": hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
    "sections": [],
    "paragraphs": [paragraph_info(p, i) for i, p in enumerate(doc.paragraphs)],
    "tables": [],
    "inline_shapes": [],
    "styles": [],
}

for i, s in enumerate(doc.sections):
    data["sections"].append({
        "index": i,
        "start_type": str(s.start_type),
        "orientation": str(s.orientation),
        "page_width": emu(s.page_width),
        "page_height": emu(s.page_height),
        "top_margin": emu(s.top_margin),
        "bottom_margin": emu(s.bottom_margin),
        "left_margin": emu(s.left_margin),
        "right_margin": emu(s.right_margin),
        "header_distance": emu(s.header_distance),
        "footer_distance": emu(s.footer_distance),
        "different_first_page_header_footer": s.different_first_page_header_footer,
        "header_paragraphs": [paragraph_info(p, j, f"section{i}.header") for j, p in enumerate(s.header.paragraphs)],
        "footer_paragraphs": [paragraph_info(p, j, f"section{i}.footer") for j, p in enumerate(s.footer.paragraphs)],
    })

for i, table in enumerate(doc.tables):
    rows = []
    for row in table.rows:
        rows.append([[paragraph_info(p, j, f"table{i}") for j, p in enumerate(cell.paragraphs)] for cell in row.cells])
    data["tables"].append({"index": i, "rows": len(table.rows), "cols": len(table.columns), "style": table.style.name if table.style else None, "content": rows})

for i, shape in enumerate(doc.inline_shapes):
    data["inline_shapes"].append({"index": i, "width": emu(shape.width), "height": emu(shape.height), "type": str(shape.type)})

used_styles = {p.style.name for p in doc.paragraphs if p.style}
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            used_styles.update(p.style.name for p in cell.paragraphs if p.style)
for name in sorted(used_styles):
    data["styles"].append(style_info(doc.styles[name]))

with ZipFile(REFERENCE) as zf:
    data["package_parts"] = [
        {"path": i.filename, "size": i.file_size, "sha256": hashlib.sha256(zf.read(i.filename)).hexdigest()}
        for i in zf.infolist()
    ]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(OUT)
