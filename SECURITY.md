# Security policy

This is a static portfolio site and does not process authentication, payments, or user-submitted data.

To report a security issue, email the contact address in [`/.well-known/security.txt`](public/.well-known/security.txt) rather than opening a public issue. Do not include credentials, personal data, or exploit payloads in public discussions.

The deployment uses Cloudflare Pages headers from `_headers`. Every push and pull request is checked for the required security headers and their values, a Content Security Policy without unsafe sources, a current `security.txt`, and committed secrets. GitHub Actions are pinned to commit SHAs, and Dependabot keeps the pins and the npm dependencies up to date.
