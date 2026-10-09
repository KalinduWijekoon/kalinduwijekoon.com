from html.parser import HTMLParser
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
errors = []


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.seen_title = False
        self.seen_description = False
        self.seen_h1 = False
        self.html_lang = None
        self.open_main = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.html_lang = values.get("lang")
        if tag == "title":
            self.seen_title = True
        if tag == "meta" and values.get("name") == "description":
            self.seen_description = bool(values.get("content"))
        if tag == "h1":
            self.seen_h1 = True
        if tag == "main":
            self.open_main += 1
        if tag == "img" and "alt" not in values:
            errors.append("Images must have alt text.")

    def handle_endtag(self, tag):
        if tag == "main":
            self.open_main -= 1


index = ROOT / "src" / "pages" / "index.astro"
headers = ROOT / "public" / "_headers"
if not index.exists():
    errors.append("src/pages/index.astro is missing.")
else:
    parser = SiteParser()
    parser.feed(index.read_text(encoding="utf-8"))
    if parser.html_lang != "en":
        errors.append("html lang must be set to en.")
    if not parser.seen_title:
        errors.append("A title element is required.")
    if not parser.seen_description:
        errors.append("A non-empty meta description is required.")
    if not parser.seen_h1:
        errors.append("A single primary h1 is required.")
    if parser.open_main != 0:
        errors.append("main element is not balanced.")

if not headers.exists():
    errors.append("_headers is missing.")
else:
    header_text = headers.read_text(encoding="utf-8")
    required_headers = (
        "Content-Security-Policy:",
        "X-Content-Type-Options:",
        "Referrer-Policy:",
        "Permissions-Policy:",
    )
    for required in required_headers:
        if required not in header_text:
            errors.append(f"Required security header missing: {required}")

for path in (ROOT / "index.html", ROOT / "styles.css", ROOT / "script.js"):
    if path.exists() and "example.com" in path.read_text(encoding="utf-8"):
        errors.append(f"Unexpected domain placeholder in {path.name}.")

if errors:
    print("Site validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Site validation passed.")
