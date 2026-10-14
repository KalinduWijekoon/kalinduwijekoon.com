import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";

// Links a file from public/ with a short hash of its contents, e.g.
// "/styles.css?v=3f9a1c2b7d". Cloudflare lets browsers cache CSS and JS for
// hours; a new hash on every change makes them fetch the new file right away
// instead of pairing fresh HTML with a stale stylesheet.
export function asset(path: string): string {
  const file = readFileSync(join(process.cwd(), "public", path));
  const hash = createHash("sha256").update(file).digest("hex").slice(0, 10);
  return `/${path}?v=${hash}`;
}
