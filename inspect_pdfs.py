import sys
import pymupdf

def inspect_pdf(path, out):
    out.write("====================================\n")
    out.write("Inspecting: " + path + "\n")
    doc = pymupdf.open(path)
    for p_no, page in enumerate(doc):
        out.write(f"--- Page {p_no + 1} (w={page.rect.width}, h={page.rect.height}) ---\n")
        blocks = page.get_text('dict')['blocks']
        for b in blocks:
            if 'lines' in b:
                for l in b['lines']:
                    line_text = "".join([s['text'] for s in l['spans']])
                    sp = l['spans'][0]
                    if len(line_text.strip()) > 0:
                        out.write(f"[{sp['bbox'][1]:.1f}] font={sp['font']}, sz={sp['size']:.1f}, col=#{sp['color']:06x}: {line_text[:70]}\n")
            elif 'image' in b:
                out.write(f"[IMG] bbox={b['bbox']}, w={b['width']}, h={b['height']}\n")

with open('extracted_ref/pdf_layout_details_utf8.txt', 'w', encoding='utf-8') as f:
    inspect_pdf(r"c:\Users\bhanu\Downloads\SHIFT_IDF_B_TNR9.pdf", f)
    inspect_pdf(r"c:\Users\bhanu\Downloads\SHIFT_Experimental_Validation.pdf", f)

