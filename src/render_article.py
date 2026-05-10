"""Render the sample longform article HTML to a matching PDF."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTICLE_HTML = PROJECT_ROOT / "docs" / "sample_article.html"
ARTICLE_PDF = PROJECT_ROOT / "docs" / "sample_article.pdf"


def find_chrome_executable() -> str:
    """Return a Chrome/Chromium executable for HTML-to-PDF rendering."""

    candidates = [
        os.environ.get("CHROME_PATH"),
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise RuntimeError(
        "Chrome or Chromium is required to render the sample article PDF. "
        "Install Chrome/Chromium or set CHROME_PATH to the executable."
    )


def render_html_to_pdf(html_path: Path = ARTICLE_HTML, pdf_path: Path = ARTICLE_PDF) -> Path:
    """Render the sample article PDF from the exact HTML article."""

    html_path = html_path.resolve()
    pdf_path = pdf_path.resolve()
    if not html_path.exists():
        raise FileNotFoundError(f"Missing article HTML: {html_path}")

    chrome = find_chrome_executable()
    command = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_path}",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=1000",
        html_path.as_uri(),
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"Chrome did not produce a PDF at {pdf_path}")
    return pdf_path


def main() -> None:
    pdf_path = render_html_to_pdf()
    print(f"Rendered sample article PDF: {pdf_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
