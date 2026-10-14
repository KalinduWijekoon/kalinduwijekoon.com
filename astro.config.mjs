import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://kalinduwijekoon.com",
  output: "static",
  build: {
    // the CSP only allows same-origin stylesheets (style-src 'self'), so the
    // font CSS must ship as a file, never as an inline <style> block
    inlineStylesheets: "never",
  },
});
