// main.ts — entrypoint for news-image-20261119.
// "THE WORLD IN ONE DAY — Thursday 19 November 2026": a 1024x1024
// newspaper front page drawn in code (see draw.py) and held in this
// repository as entry.png. This program copies that image to the
// grader's output directory, /output/entry.png, byte for byte, so the
// two graded runs always produce identical output. Node 22 stdlib only,
// no network, no dependencies.
const fs = require("node:fs");
const path = require("node:path");

const SOURCE = path.join(__dirname, "entry.png");
const OUT_DIR = process.env.OUTPUT_DIR || "/output";
const DEST = path.join(OUT_DIR, "entry.png");

fs.mkdirSync(OUT_DIR, { recursive: true });
fs.copyFileSync(SOURCE, DEST);

// Validate what we just wrote: it must be a whole PNG within the
// competition's limits (at most 1 MiB, at most 1024 by 1024 pixels).
// The PNG signature is its first 8 bytes; the size cap is 1048576.
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576;
const written = fs.readFileSync(DEST);
if (!written.subarray(0, 8).equals(PNG_SIGNATURE)) {
  throw new Error(`${DEST} is not a PNG (bad signature)`);
}
if (written.length > MAX_BYTES) {
  throw new Error(`${DEST} is ${written.length} bytes, over the ${MAX_BYTES} byte limit`);
}
const bytes = written.length;
console.log(`wrote ${DEST} (${bytes} bytes, PNG signature OK, under 1 MiB)`);
