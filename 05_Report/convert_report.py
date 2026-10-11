from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
REPORT_MD = ROOT / "project_report.md"
DOCX_OUT = ROOT / "project_report.docx"
PDF_OUT = ROOT / "project_report.pdf"


def require_pandoc():
    if shutil.which("pandoc") is None:
        raise RuntimeError(
            "pandoc is not installed or not on PATH. "
            "Install pandoc first: https://pandoc.org/installing.html"
        )


def run(cmd):
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def convert_to_docx():
    cmd = [
        "pandoc",
        str(REPORT_MD),
        "-o",
        str(DOCX_OUT),
        "--standalone",
        "--toc",
        "--number-sections",
        "--from=gfm",
        "--embed-resources",
        "--resource-path",
        str(ROOT.parent),
    ]
    run(cmd)


def convert_to_pdf():
    # Try common PDF engines in order.
    engine_candidates = [
        "weasyprint",
        "wkhtmltopdf",
        "xelatex",
        "pdflatex",
    ]

    available = [e for e in engine_candidates if shutil.which(e)]
    if not available:
        raise RuntimeError(
            "No supported PDF engine was found. Install one of: "
            "weasyprint, wkhtmltopdf, xelatex, or pdflatex"
        )

    # We prefer weasyprint if available because it works well for modern HTML/PDF conversion.
    chosen_engine = available[0]
    if chosen_engine == "weasyprint":
        cmd = [
            "pandoc",
            str(REPORT_MD),
            "-o",
            str(PDF_OUT),
            "--standalone",
            "--toc",
            "--number-sections",
            "--from=gfm",
            "--pdf-engine=weasyprint",
            "--resource-path",
            str(ROOT.parent),
        ]
        run(cmd)
        return

    if chosen_engine == "wkhtmltopdf":
        cmd = [
            "pandoc",
            str(REPORT_MD),
            "-o",
            str(PDF_OUT),
            "--standalone",
            "--toc",
            "--number-sections",
            "--from=gfm",
            "--pdf-engine=wkhtmltopdf",
            "--resource-path",
            str(ROOT.parent),
        ]
        run(cmd)
        return

    # LaTeX fallback:
    cmd = [
        "pandoc",
        str(REPORT_MD),
        "-o",
        str(PDF_OUT),
        "--standalone",
        "--toc",
        "--number-sections",
        "--from=gfm",
        "--pdf-engine",
        chosen_engine,
        "--resource-path",
        str(ROOT.parent),
    ]
    run(cmd)


def main():
    if not REPORT_MD.exists():
        raise FileNotFoundError(f"Markdown report not found: {REPORT_MD}")

    require_pandoc()

    print("Converting markdown report to DOCX...")
    convert_to_docx()
    print(f"Created: {DOCX_OUT}")

    print("Converting markdown report to PDF...")
    convert_to_pdf()
    print(f"Created: {PDF_OUT}")

    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Conversion failed: {exc}")
        sys.exit(1)
