#!/usr/bin/env node
/**
 * Merge five LC Actual Test packs per level into one 50-question practice.
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const LEVELS = [
  {
    prefix: "bas",
    level: "basic",
    dir: "data/basic/lc",
    practiceId: "bas-lc-at",
    audioRef: "bas-lc-at",
    packs: [
      "bas-lc-at-q01-10",
      "bas-lc-at-q11-20",
      "bas-lc-at-q21-30",
      "bas-lc-at-q31-40",
      "bas-lc-at-q41-50",
    ],
  },
  {
    prefix: "int",
    level: "intermediate",
    dir: "data/intermediate/lc",
    practiceId: "int-lc-at",
    audioRef: "int-lc-at",
    packs: [
      "int-lc-at-q01-10",
      "int-lc-at-q11-20",
      "int-lc-at-q21-30",
      "int-lc-at-q31-40",
      "int-lc-at-q41-50",
    ],
  },
  {
    prefix: "adv",
    level: "advanced",
    dir: "data/advanced/lc",
    practiceId: "adv-lc-at",
    audioRef: "adv-lc-at",
    packs: [
      "adv-lc-at-q01-10",
      "adv-lc-at-q11-20",
      "adv-lc-at-q21-30",
      "adv-lc-at-q31-40",
      "adv-lc-at-q41-50",
    ],
  },
];

function mergeLevel(cfg) {
  const items = [];
  let qNum = 0;
  for (const packId of cfg.packs) {
    const filePath = path.join(ROOT, cfg.dir, `${packId}.json`);
    const pack = JSON.parse(fs.readFileSync(filePath, "utf8"));
    for (const item of pack.items) {
      qNum++;
      items.push({
        ...item,
        id: `q${qNum}`,
        label: String(item.label ?? qNum),
      });
    }
  }
  if (items.length !== 50) {
    throw new Error(`${cfg.practiceId}: expected 50 items, got ${items.length}`);
  }
  const merged = {
    practiceId: cfg.practiceId,
    title: "LC Actual Test",
    subtitle: "Questions 01–50",
    level: cfg.level,
    skill: "lc",
    stub: false,
    audioRef: cfg.audioRef,
    introEn: "Listening Actual Test — choose the best answer for each question.",
    items,
  };
  const outPath = path.join(ROOT, cfg.dir, `${cfg.practiceId}.json`);
  fs.writeFileSync(outPath, JSON.stringify(merged, null, 2) + "\n");
  console.log(`Wrote ${outPath} (${items.length} items)`);
  for (const packId of cfg.packs) {
    fs.unlinkSync(path.join(ROOT, cfg.dir, `${packId}.json`));
    console.log(`Deleted ${packId}.json`);
  }
  return { practiceId: cfg.practiceId, count: items.length, cfg };
}

function catalogEntry(cfg) {
  return {
    id: cfg.practiceId,
    level: cfg.level,
    skill: "lc",
    group: "LC Actual Test",
    title: "LC Actual Test",
    subtitle: "Questions 01–50",
    audioRef: cfg.audioRef,
    dataPath: `${cfg.dir}/${cfg.practiceId}.json`,
    stub: false,
  };
}

function updateCatalog() {
  const catalogPath = path.join(ROOT, "data/catalog.json");
  const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));

  const removeIds = new Set();
  for (const cfg of LEVELS) {
    for (const packId of cfg.packs) removeIds.add(packId);
  }

  for (const track of catalog.tracks) {
    if (track.skill !== "lc") continue;
    const isLcAt = (p) => removeIds.has(p.id) || p.id.endsWith("-lc-at");
    const hadAt = track.practices.some((p) => removeIds.has(p.id));
    if (!hadAt) continue;
    track.practices = track.practices.filter((p) => !removeIds.has(p.id));
    const cfg = LEVELS.find((c) => c.level === track.level);
    if (cfg) track.practices.push(catalogEntry(cfg));
  }

  for (const id of removeIds) {
    delete catalog.practiceIndex[id];
  }
  for (const cfg of LEVELS) {
    catalog.practiceIndex[cfg.practiceId] = catalogEntry(cfg);
  }

  fs.writeFileSync(catalogPath, JSON.stringify(catalog, null, 2) + "\n");
  const count = Object.keys(catalog.practiceIndex).length;
  console.log(`Updated catalog.json — practiceIndex count: ${count}`);
  return count;
}

for (const cfg of LEVELS) mergeLevel(cfg);
const count = updateCatalog();
if (count !== 117) {
  console.warn(`WARNING: expected 117 practices, got ${count}`);
  process.exit(1);
}
