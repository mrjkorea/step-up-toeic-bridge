#!/usr/bin/env node
/**
 * Import items-v2 pack: copy practice JSON + merge catalog + extras.
 * Usage: node scripts/import-content-v2.mjs <path-to-items-v2>
 */
import fs from "fs";
import path from "path";

const packRoot = process.argv[2];
if (!packRoot) {
  console.error("Usage: node scripts/import-content-v2.mjs <items-v2-dir>");
  process.exit(1);
}

const repoRoot = path.resolve(path.dirname(import.meta.url.replace("file://", "")), "..");
const dataRoot = path.join(repoRoot, "data");

const LEVEL_MAP = { bas: "basic", int: "intermediate", adv: "advanced" };

function skillFromId(id) {
  if (id.includes("-lc-")) return "lc";
  if (id.includes("-rc-")) return "rc";
  throw new Error(`Cannot infer skill from id: ${id}`);
}

function destPath(levelKey, filename) {
  const level = LEVEL_MAP[levelKey];
  const skill = skillFromId(filename.replace(/\.json$/, ""));
  return path.join(dataRoot, level, skill, filename);
}

function copyPractices() {
  let catalogCount = 0;
  let extraCount = 0;
  for (const levelKey of ["bas", "int", "adv"]) {
    const dir = path.join(packRoot, levelKey);
    for (const file of fs.readdirSync(dir)) {
      if (!file.endsWith(".json")) continue;
      const isExtra = file.includes("-warmup") || file.includes("-checkup");
      const src = path.join(dir, file);
      const dest = destPath(levelKey, file);
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.copyFileSync(src, dest);
      if (isExtra) extraCount++;
      else catalogCount++;
    }
  }
  return { catalogCount, extraCount };
}

function trackIdFor(level, skill) {
  return `${level}-${skill}`;
}

function catalogEntryFromExtra(extra, parent) {
  const entry = {
    id: extra.id,
    level: extra.level,
    skill: extra.skill,
    group: parent?.group ?? extra.group ?? "",
    title: extra.title,
    subtitle: parent?.subtitle ?? extra.block ?? "",
    audioRef: extra.audioRef,
    dataPath: extra.dataPath,
    stub: false,
  };
  if (parent?.photoDir && extra.block === "Warm-Up") {
    entry.photoDir = parent.photoDir;
  }
  return entry;
}

function mergeExtrasIntoCatalog(catalog, extrasDoc) {
  const byParent = new Map();
  for (const extra of extrasDoc.practices || []) {
    const list = byParent.get(extra.parent) || { warmup: [], checkup: [] };
    if (extra.block === "Warm-Up") list.warmup.push(extra);
    else if (extra.block === "Check-Up") list.checkup.push(extra);
    else list.checkup.push(extra);
    byParent.set(extra.parent, list);
  }

  for (const track of catalog.tracks) {
    const indexById = new Map(track.practices.map((p, i) => [p.id, i]));
    const parentMeta = new Map(track.practices.map((p) => [p.id, p]));
    const merged = [];
    for (const p of track.practices) {
      const extras = byParent.get(p.id);
      if (extras?.warmup?.length) {
        for (const ex of extras.warmup) {
          merged.push(catalogEntryFromExtra(ex, p));
        }
      }
      merged.push(p);
      if (extras?.checkup?.length) {
        for (const ex of extras.checkup) {
          merged.push(catalogEntryFromExtra(ex, p));
        }
      }
    }
    track.practices = merged;
  }

  catalog.practiceIndex = Object.fromEntries(
    catalog.tracks.flatMap((t) => t.practices.map((p) => [p.id, p]))
  );
}

function main() {
  const catalogSrc = path.join(packRoot, "catalog.json");
  const extraSrc = path.join(packRoot, "CATALOG_EXTRA.json");
  const { catalogCount, extraCount } = copyPractices();

  const catalog = JSON.parse(fs.readFileSync(catalogSrc, "utf8"));
  const extrasDoc = JSON.parse(fs.readFileSync(extraSrc, "utf8"));
  mergeExtrasIntoCatalog(catalog, extrasDoc);

  fs.writeFileSync(path.join(dataRoot, "catalog.json"), JSON.stringify(catalog, null, 2) + "\n");

  const verifySrc = path.join(path.dirname(packRoot), "VERIFY_2026-10-28.md");
  const verifyAlt = path.join(packRoot, "VERIFY_2026-10-28.md");
  const verifyFrom = fs.existsSync(verifySrc) ? verifySrc : verifyAlt;
  const docsDir = path.join(repoRoot, "docs");
  fs.mkdirSync(docsDir, { recursive: true });
  fs.copyFileSync(verifyFrom, path.join(docsDir, "VERIFY_2026-10-28.md"));

  console.log(JSON.stringify({ catalogCount, extraCount, version: catalog.version, practicesInCatalog: Object.keys(catalog.practiceIndex).length }, null, 2));
}

main();
