# Cloud Security Engineer portfolio

Personal portfolio for Kalindu Wijekoon, a cloud security engineer. It is a static Astro site on Cloudflare Pages, kept small so it can be reviewed, deployed, and secured with a minimal attack surface.

The hero is a 3D scene of a protected cloud region: a dome shielding cloud workloads, a posture scanner that flags and auto-remediates misconfigured resources, and threats deflected off the perimeter. It is built entirely with CSS 3D transforms and inline SVG, with no WebGL, canvas, or animation libraries.

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

The reference projects are labelled as illustrative; replace them with real write-ups as they are published.

## Project layout

- `src/pages/index.astro`: the single page, including the hero scene markup.
- `public/styles.css`: all styles and animations.
- `public/script.js`: mobile menu, scroll reveals, pointer parallax, and pausing animations when they are off screen.
- `public/_headers`: security headers for Cloudflare Pages.

Fonts (Inter and Sora) are self-hosted through Fontsource, so they satisfy the `font-src 'self'` policy.

## Motion and accessibility

- With `prefers-reduced-motion`, the hero shows a still frame and the scroll and hover animations are off.
- Animations pause when their section is scrolled out of view.
- Hover effects on the sky clouds are disabled on touch screens.

## Security and quality

- `_headers` applies restrictive browser security headers on Cloudflare Pages.
- The GitHub workflow checks the Astro build, required files, HTML structure, security-header configuration, and secrets.
- The site has no third-party scripts, hosted fonts, trackers, forms, or runtime services.
