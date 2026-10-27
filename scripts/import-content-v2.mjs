#!/usr/bin/env node
/**
 * Import items-v2 pack: copy practice JSON into data/ and refresh catalog.
 * Warm-Up / Check-Up JSON files are merged into their parent section file (not separate catalog rows).
 * Usage: node scripts/import-content-v2.mjs <path-to-items-v2>
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { spawnSync } from "child_process";

const packRoot = process.argv[2];
if (!packRoot) {
  console.error("Usage: node scripts/import-content-v2.mjs <items-v2-dir>");
  process.exit(1);
}

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
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

function main() {
  const catalogSrc = path.join(packRoot, "catalog.json");
  const { catalogCount, extraCount } = copyPractices();

  const catalog = JSON.parse(fs.readFileSync(catalogSrc, "utf8"));
  fs.writeFileSync(path.join(dataRoot, "catalog.json"), JSON.stringify(catalog, null, 2) + "\n");

  const mergeScript = path.join(repoRoot, "scripts", "merge-section-extras.mjs");
  const mergeResult = spawnSync(process.execPath, [mergeScript], { stdio: "inherit" });
  if (mergeResult.status !== 0) process.exit(mergeResult.status || 1);

  const verifySrc = path.join(path.dirname(packRoot), "VERIFY_2026-10-28.md");
  const verifyAlt = path.join(packRoot, "VERIFY_2026-10-28.md");
  const verifyFrom = fs.existsSync(verifySrc) ? verifySrc : verifyAlt;
  if (fs.existsSync(verifyFrom)) {
    const docsDir = path.join(repoRoot, "docs");
    fs.mkdirSync(docsDir, { recursive: true });
    fs.copyFileSync(verifyFrom, path.join(docsDir, "VERIFY_2026-10-28.md"));
  }

  const finalCatalog = JSON.parse(fs.readFileSync(path.join(dataRoot, "catalog.json"), "utf8"));
  console.log(
    JSON.stringify(
      {
        catalogCount,
        extraCount,
        version: finalCatalog.version,
        practicesInCatalog: Object.keys(finalCatalog.practiceIndex).length,
      },
      null,
      2
    )
  );
}

main();
