# Cloud Security Engineer portfolio

An Astro static portfolio starter for Cloudflare Pages. The site remains mostly static so it can be reviewed, deployed, and secured with a small attack surface.

## Install and local development

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Then open the local URL shown by Astro, normally `http://localhost:4321`.

Create a production build and preview it:

```powershell
npm run build
npm run preview
```

## Cloudflare Pages

1. Push this directory to a GitHub repository.
2. In Cloudflare, open **Workers & Pages → Create application → Pages → Connect to Git**.
3. Select the repository and use:
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
   - **Production branch:** `main`
4. After the first deployment, open **Custom domains** and add the domain managed in Cloudflare.
5. Confirm HTTPS is active and test the response headers with a browser or `curl -I https://your-domain.example`.

Replace `example.com` in `index.html`, `robots.txt`, and any future sitemap with the real domain before launch. Replace sample email addresses and case studies with verified personal content.

## Security and quality

- `_headers` applies restrictive browser security headers on Cloudflare Pages.
- The GitHub workflow checks the Astro build, required files, HTML structure, security-header configuration, and secrets.
- The site has no third-party scripts, fonts, trackers, forms, or runtime services by default.
