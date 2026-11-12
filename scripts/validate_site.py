from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import os
import re
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
    # Read "Name: value" lines into a dict, so the checks below look at what
    # each header is set to and not only at whether its name appears.
    header_values = {}
    for line in headers.read_text(encoding="utf-8").splitlines():
        name, colon, value = line.strip().partition(":")
        if colon and not name.startswith("#"):
            header_values.setdefault(name.strip().lower(), value.strip())

    for required in (
        "Content-Security-Policy",
        "Strict-Transport-Security",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Permissions-Policy",
    ):
        if required.lower() not in header_values:
            errors.append(f"Required security header missing: {required}")

    expected_values = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
    }
    for name, expected in expected_values.items():
        value = header_values.get(name.lower())
        if value is not None and value != expected:
            errors.append(f"{name} must be {expected}, found: {value}")

    hsts = header_values.get("strict-transport-security", "")
    max_age = re.search(r"max-age=(\d+)", hsts)
    if hsts and (not max_age or int(max_age.group(1)) < 31536000):
        errors.append("Strict-Transport-Security max-age must be at least a year.")

    # Split the CSP into {directive: [sources]} and reject anything that
    # would quietly weaken it.
    csp = {}
    for part in header_values.get("content-security-policy", "").split(";"):
        tokens = part.split()
        if tokens:
            csp[tokens[0].lower()] = tokens[1:]
    if csp:
        unsafe_sources = ("'unsafe-inline'", "'unsafe-eval'", "*", "http:", "https:")
        for directive, sources in csp.items():
            for source in sources:
                if source in unsafe_sources:
                    errors.append(f"CSP {directive} must not allow {source}.")
        if "data:" in csp.get("script-src", csp.get("default-src", [])):
            errors.append("CSP must not allow data: URLs as scripts.")
        required_directives = {
            "default-src": ["'self'"],
            "script-src": ["'self'"],
            "object-src": ["'none'"],
            "base-uri": ["'self'"],
            "frame-ancestors": ["'none'"],
        }
        for directive, expected in required_directives.items():
            if csp.get(directive) != expected:
                errors.append(
                    f"CSP {directive} must be exactly: {' '.join(expected)}"
                )

# security.txt (RFC 9116) must exist, name a contact, and not be expired.
security_txt = ROOT / "public" / ".well-known" / "security.txt"
if not security_txt.exists():
    errors.append("public/.well-known/security.txt is missing.")
else:
    fields = {}
    for line in security_txt.read_text(encoding="utf-8").splitlines():
        name, colon, value = line.partition(":")
        if colon and not name.startswith("#"):
            fields.setdefault(name.strip().lower(), value.strip())
    if not fields.get("contact"):
        errors.append("security.txt needs a Contact field.")
    try:
        expires = datetime.fromisoformat(fields["expires"].replace("Z", "+00:00"))
        if expires <= datetime.now(timezone.utc):
            errors.append("security.txt has expired; set a new Expires date.")
    except (KeyError, ValueError, TypeError):
        errors.append("security.txt needs an Expires field with a time zone.")

# No leftover template domains in anything that ships.
shipped = list(pages)
for pattern in ("*.js", "*.css", "*.txt", "*.xml"):
    shipped.extend((ROOT / "public").rglob(pattern))
for path in shipped:
    if "example.com" in path.read_text(encoding="utf-8"):
        errors.append(f"Unexpected domain placeholder in {path.name}.")

if errors:
    print("Site validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Site validation passed.")
