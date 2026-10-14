from html.parser import HTMLParser
from pathlib import Path
import os
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


class InlineCodeParser(HTMLParser):
    """Finds inline code that the CSP (script-src/style-src 'self') blocks."""

    def __init__(self):
        super().__init__()
        self.found = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "style":
            self.found.append("an inline <style> block")
        if tag == "script" and not values.get("src"):
            self.found.append("an inline <script> block")
        if "style" in values:
            self.found.append(f'a style="" attribute on <{tag}>')
        for name, _ in attrs:
            if name.startswith("on"):
                self.found.append(f"an inline {name}= handler on <{tag}>")


pages = sorted((ROOT / "src" / "pages").glob("*.astro"))
headers = ROOT / "public" / "_headers"
if not (ROOT / "src" / "pages" / "index.astro").exists():
    errors.append("src/pages/index.astro is missing.")
for page in pages:
    name = page.name
    parser = SiteParser()
    parser.feed(page.read_text(encoding="utf-8"))
    if parser.html_lang != "en":
        errors.append(f"{name}: html lang must be set to en.")
    if not parser.seen_title:
        errors.append(f"{name}: a title element is required.")
    if not parser.seen_description:
        errors.append(f"{name}: a non-empty meta description is required.")
    if not parser.seen_h1:
        errors.append(f"{name}: a single primary h1 is required.")
    if parser.open_main != 0:
        errors.append(f"{name}: main element is not balanced.")

# The CSP blocks inline code without any visible error, so check what the
# build actually ships (Astro can inline small CSS and scripts on its own).
dist = ROOT / "dist"
built = sorted(dist.rglob("*.html")) if dist.exists() else []
if not built:
    if os.environ.get("CI"):
        errors.append("dist/ has no HTML pages; run the build before validating.")
    else:
        print("Note: no build in dist/, skipped the inline-code check.")
for page in built:
    parser = InlineCodeParser()
    parser.feed(page.read_text(encoding="utf-8"))
    for item in sorted(set(parser.found)):
        errors.append(
            f"dist/{page.relative_to(dist)} has {item}, which the CSP blocks."
        )

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
