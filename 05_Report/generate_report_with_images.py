#!/usr/bin/env python3
"""
Convert the project markdown report to DOCX and PDF with embedded images.

Prerequisites:
- python-docx (pip install python-docx)
- pypandoc (pip install pypandoc) - optional for PDF
- Pillow (pip install Pillow)

Usage:
    python3 05_Report/generate_report_with_images.py
"""

from pathlib import Path
import sys
import re
from io import BytesIO

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("ERROR: python-docx is not installed.")
    print("Install it with: pip install python-docx")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("WARNING: Pillow is not installed. Image processing may fail.")
    print("Install it with: pip install Pillow")


ROOT = Path(__file__).resolve().parent
REPORT_MD = ROOT / "project_report.md"
DOCX_OUT = ROOT / "project_report.docx"
PDF_OUT = ROOT / "project_report.pdf"


def get_image_path(md_image_path):
    """Resolve image path from markdown reference."""
    # Handle relative paths like ../03_Charts/sentiment_analysis.png
    if md_image_path.startswith('../'):
        return ROOT.parent / md_image_path[3:]
    elif md_image_path.startswith('./'):
        return ROOT / md_image_path[2:]
    else:
        return ROOT.parent / md_image_path


def add_heading_with_level(doc, text, level):
    """Add a heading with the appropriate level (1-9)."""
    doc.add_heading(text, level=min(level, 9))


def add_table_from_markdown(doc, md_table_text):
    """Parse a markdown table and add it to the document."""
    lines = md_table_text.strip().split('\n')
    if len(lines) < 3:
        doc.add_paragraph("(Invalid table format)")
        return
    
    # Extract headers
    headers = [h.strip() for h in lines[0].split('|')[1:-1]]
    
    # Skip separator line
    # Extract rows
    rows = []
    for line in lines[2:]:
        if line.strip():
            row = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(row) == len(headers):
                rows.append(row)
    
    if not rows:
        doc.add_paragraph("(No table rows found)")
        return
    
    # Create table
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.style = 'Light Grid Accent 1'
    
    # Add headers
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        # Style header
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
    
    # Add rows
    for row_idx, row in enumerate(rows):
        for col_idx, cell_text in enumerate(row):
            table.rows[row_idx + 1].cells[col_idx].text = cell_text


def process_markdown_to_docx_with_images(md_path, docx_path):
    """Convert markdown report to DOCX with formatting and embedded images."""
    
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown report not found: {md_path}")
    
    doc = Document()
    
    # Set margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by lines
    lines = content.split('\n')
    current_paragraph_lines = []
    heading_level_map = {'#': 1, '##': 2, '###': 3, '####': 4, '#####': 5, '######': 6}
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for heading
        if line.startswith('#'):
            # Flush current paragraph
            if current_paragraph_lines:
                para_text = '\n'.join(current_paragraph_lines).strip()
                if para_text:
                    doc.add_paragraph(para_text)
                current_paragraph_lines = []
            
            # Extract heading level and text
            heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
            if heading_match:
                hashes = heading_match.group(1)
                heading_text = heading_match.group(2)
                level = len(hashes)
                add_heading_with_level(doc, heading_text, level)
        
        # Check for table
        elif line.strip().startswith('|'):
            # Flush current paragraph
            if current_paragraph_lines:
                para_text = '\n'.join(current_paragraph_lines).strip()
                if para_text:
                    doc.add_paragraph(para_text)
                current_paragraph_lines = []
            
            # Collect table lines
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            i -= 1
            
            table_text = '\n'.join(table_lines)
            add_table_from_markdown(doc, table_text)
        
        # Check for code block
        elif line.strip().startswith('```'):
            # Flush current paragraph
            if current_paragraph_lines:
                para_text = '\n'.join(current_paragraph_lines).strip()
                if para_text:
                    doc.add_paragraph(para_text)
                current_paragraph_lines = []
            
            # Collect code block
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            
            if code_lines:
                code_para = doc.add_paragraph()
                code_para.paragraph_format.left_indent = Inches(0.5)
                for code_line in code_lines:
                    if code_line.strip():
                        run = code_para.add_run(code_line + '\n')
                        run.font.name = 'Courier New'
                        run.font.size = Pt(9)
        
        # Check for image reference
        elif '![' in line and ']' in line:
            # Flush current paragraph
            if current_paragraph_lines:
                para_text = '\n'.join(current_paragraph_lines).strip()
                if para_text:
                    doc.add_paragraph(para_text)
                current_paragraph_lines = []
            
            # Extract image info
            img_match = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if img_match:
                alt_text = img_match.group(1)
                img_path_str = img_match.group(2)
                
                # Resolve image path
                full_path = get_image_path(img_path_str)
                
                if full_path.exists():
                    try:
                        # Add image with max width 5.5 inches
                        doc.add_picture(str(full_path), width=Inches(5.5))
                        # Add caption
                        caption = doc.add_paragraph(alt_text)
                        caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        caption_run = caption.runs[0]
                        caption_run.font.italic = True
                        caption_run.font.size = Pt(10)
                        print(f"✓ Embedded image: {full_path.name}")
                    except Exception as e:
                        error_msg = f"[Image: {alt_text}] (Could not embed: {e})"
                        doc.add_paragraph(error_msg)
                        print(f"✗ Failed to embed {full_path.name}: {e}")
                else:
                    error_msg = f"[Image: {alt_text}]\n(File not found at: {full_path})"
                    doc.add_paragraph(error_msg)
                    print(f"✗ Image not found: {full_path}")
        
        # Regular text
        elif line.strip():
            current_paragraph_lines.append(line)
        
        # Blank line - flush paragraph
        elif current_paragraph_lines:
            para_text = '\n'.join(current_paragraph_lines).strip()
            if para_text:
                doc.add_paragraph(para_text)
            current_paragraph_lines = []
        
        i += 1
    
    # Flush remaining paragraph
    if current_paragraph_lines:
        para_text = '\n'.join(current_paragraph_lines).strip()
        if para_text:
            doc.add_paragraph(para_text)
    
    # Save document
    doc.save(docx_path)
    print(f"✓ DOCX report created: {docx_path}")


def generate_pdf_from_docx():
    """Generate PDF from DOCX using LibreOffice or pandoc."""
    import subprocess
    import shutil
    
    # Try LibreOffice first (most reliable for DOCX -> PDF)
    if shutil.which('libreoffice'):
        print("\n[2/2] Converting DOCX to PDF using LibreOffice...")
        try:
            subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                str(DOCX_OUT),
                '--outdir', str(ROOT)
            ], check=True, capture_output=True)
            print(f"✓ PDF report created: {PDF_OUT}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ LibreOffice conversion failed: {e}")
    
    # Try pandoc with weasyprint
    if shutil.which('pandoc'):
        print("\n[2/2] Converting markdown to PDF using pandoc...")
        try:
            subprocess.run([
                'pandoc',
                str(REPORT_MD),
                '-o', str(PDF_OUT),
                '--pdf-engine=weasyprint',
                '--standalone',
                '--toc',
                '--number-sections',
            ], check=True, capture_output=True)
            print(f"✓ PDF report created: {PDF_OUT}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Pandoc conversion failed: {e}")
    
    return False


def main():
    print("=" * 70)
    print("Project Report Conversion Tool (With Embedded Images)")
    print("=" * 70)
    
    # Generate DOCX with images
    print("\n[1/2] Converting markdown to DOCX with embedded images...")
    try:
        process_markdown_to_docx_with_images(REPORT_MD, DOCX_OUT)
    except Exception as e:
        print(f"✗ DOCX conversion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Attempt PDF generation
    pdf_success = generate_pdf_from_docx()
    
    if not pdf_success:
        print("\n[2/2] PDF Conversion Instructions")
        print("-" * 70)
        print("The DOCX file was created successfully with embedded images.")
        print("To generate a PDF, use one of these methods:")
        print("")
        print("Option A: LibreOffice (recommended)")
        print("  libreoffice --headless --convert-to pdf 05_Report/project_report.docx --outdir 05_Report/")
        print("")
        print("Option B: Pandoc + WeasyPrint")
        print("  pip install weasyprint")
        print("  pandoc 05_Report/project_report.md -o 05_Report/project_report.pdf --pdf-engine=weasyprint")
        print("")
        print("Option C: Open DOCX in Microsoft Word and Save As PDF")
        print("-" * 70)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ DOCX with images: {DOCX_OUT}")
    if pdf_success:
        print(f"✓ PDF report: {PDF_OUT}")
    else:
        print(f"⚠ PDF report: Not yet generated (see instructions above)")
    print("=" * 70)


if __name__ == "__main__":
    main()
