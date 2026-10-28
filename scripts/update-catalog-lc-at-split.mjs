#!/usr/bin/env node
/** One-off: replace single LC Actual Test practices with 5×10 chunks in catalog.json */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const catalogPath = path.join(ROOT, "data/catalog.json");

const CHUNKS = [
  { idSuffix: "q01-10", titleRange: "01–10", bookRange: "Q01–10" },
  { idSuffix: "q11-20", titleRange: "11–20", bookRange: "Q11–20" },
  { idSuffix: "q21-30", titleRange: "21–30", bookRange: "Q21–30" },
  { idSuffix: "q31-40", titleRange: "31–40", bookRange: "Q31–40" },
  { idSuffix: "q41-50", titleRange: "41–50", bookRange: "Q41–50" },
];

const LEVELS = [
  { prefix: "bas", level: "basic", dataDir: "data/basic/lc" },
  { prefix: "int", level: "intermediate", dataDir: "data/intermediate/lc" },
  { prefix: "adv", level: "advanced", dataDir: "data/advanced/lc" },
];

function chunkPractices(cfg) {
  const audioRef = `${cfg.prefix}-lc-at`;
  return CHUNKS.map((c) => {
    const id = `${cfg.prefix}-lc-at-${c.idSuffix}`;
    return {
      id,
      level: cfg.level,
      skill: "lc",
      group: "LC Actual Test",
      title: `LC Actual Test · Questions ${c.titleRange}`,
      subtitle: `10 questions (book ${c.bookRange})`,
      audioRef,
      dataPath: `${cfg.dataDir}/${id}.json`,
      stub: false,
    };
  });
}

const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));

for (const cfg of LEVELS) {
  const singleId = `${cfg.prefix}-lc-at`;
  const trackId = `${cfg.level}-lc`;
  const track = catalog.tracks.find((t) => t.trackId === trackId);
  if (!track) throw new Error(`track ${trackId} missing`);
  const idx = track.practices.findIndex((p) => p.id === singleId);
  if (idx === -1) throw new Error(`${singleId} not in ${trackId}`);
  track.practices.splice(idx, 1, ...chunkPractices(cfg));
  delete catalog.practiceIndex[singleId];
  for (const p of chunkPractices(cfg)) {
    catalog.practiceIndex[p.id] = { ...p };
  }
}

const count = Object.keys(catalog.practiceIndex).length;
if (count !== 129) {
  console.warn(`practiceIndex count is ${count}, expected 129`);
}

fs.writeFileSync(catalogPath, JSON.stringify(catalog, null, 2) + "\n");
console.log("Updated catalog.json; practiceIndex entries:", count);
