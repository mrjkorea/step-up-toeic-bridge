#!/usr/bin/env node
/**
 * Merge *-warmup.json and *-checkup.json items into parent section JSON;
 * strip those practices from catalog.json.
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataRoot = path.join(repoRoot, "data");

const SECTION_MAIN = "Test Your Skills";
const SECTION_WARMUP = "Warm-Up";
const SECTION_CHECKUP = "Check-Up";

function listExtraFiles() {
  const files = [];
  for (const level of ["basic", "intermediate", "advanced"]) {
    for (const skill of ["lc", "rc"]) {
      const dir = path.join(dataRoot, level, skill);
      if (!fs.existsSync(dir)) continue;
      for (const name of fs.readdirSync(dir)) {
        if (name.endsWith("-warmup.json") || name.endsWith("-checkup.json")) {
          files.push(path.join(dir, name));
        }
      }
    }
  }
  return files;
}

function parentIdFromExtraPath(filePath) {
  const base = path.basename(filePath, ".json");
  if (base.endsWith("-warmup")) return base.replace(/-warmup$/, "");
  if (base.endsWith("-checkup")) return base.replace(/-checkup$/, "");
  return null;
}

function parentDataPath(parentId, extraPath) {
  const dir = path.dirname(extraPath);
  return path.join(dir, `${parentId}.json`);
}

function tagItems(items, section) {
  return (items || []).map((item) => ({ ...item, section }));
}

function renumberItems(items) {
  return items.map((item, idx) => ({
    ...item,
    id: `q${idx + 1}`,
    label: String(idx + 1),
  }));
}

function mergeParentFile(parentPath, warmupPath, checkupPath) {
  const parent = JSON.parse(fs.readFileSync(parentPath, "utf8"));
  const chunks = [];

  if (warmupPath && fs.existsSync(warmupPath)) {
    const warm = JSON.parse(fs.readFileSync(warmupPath, "utf8"));
    chunks.push(...tagItems(warm.items, SECTION_WARMUP));
  }

  chunks.push(...tagItems(parent.items, SECTION_MAIN));

  if (checkupPath && fs.existsSync(checkupPath)) {
    const check = JSON.parse(fs.readFileSync(checkupPath, "utf8"));
    chunks.push(...tagItems(check.items, SECTION_CHECKUP));
  }

  parent.items = renumberItems(chunks);
  fs.writeFileSync(parentPath, JSON.stringify(parent, null, 1) + "\n");
}

function stripCatalog(catalog) {
  for (const track of catalog.tracks) {
    track.practices = track.practices.filter((p) => {
      const id = p.id || "";
      return !id.endsWith("-warmup") && !id.endsWith("-checkup");
    });
  }
  catalog.practiceIndex = Object.fromEntries(
    catalog.tracks.flatMap((t) => t.practices.map((p) => [p.id, p]))
  );
}

function main() {
  const byParent = new Map();
  for (const file of listExtraFiles()) {
    const parentId = parentIdFromExtraPath(file);
    if (!parentId) continue;
    const entry = byParent.get(parentId) || { parentPath: null, warmup: null, checkup: null };
    entry.parentPath = parentDataPath(parentId, file);
    if (file.endsWith("-warmup.json")) entry.warmup = file;
    else entry.checkup = file;
    byParent.set(parentId, entry);
  }

  let merged = 0;
  for (const [, spec] of byParent) {
    if (!spec.parentPath || !fs.existsSync(spec.parentPath)) {
      console.warn("Missing parent for extras:", spec);
      continue;
    }
    mergeParentFile(spec.parentPath, spec.warmup, spec.checkup);
    merged++;
    if (spec.warmup) fs.unlinkSync(spec.warmup);
    if (spec.checkup) fs.unlinkSync(spec.checkup);
  }

  const catalogPath = path.join(dataRoot, "catalog.json");
  const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));
  stripCatalog(catalog);
  fs.writeFileSync(catalogPath, JSON.stringify(catalog, null, 2) + "\n");

  const count = Object.keys(catalog.practiceIndex).length;
  console.log(JSON.stringify({ mergedParents: merged, practicesInCatalog: count }, null, 2));
  if (count !== 129) {
    console.error(`Expected 129 practices, got ${count}`);
    process.exit(1);
  }
}

main();
