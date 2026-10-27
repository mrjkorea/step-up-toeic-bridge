#!/usr/bin/env node
/**
 * Import YBM content pack items into data/<level>/<skill>/<practiceId>.json
 * and refresh catalog stub flags + Part II subtitles (Basic).
 *
 * Usage: node scripts/import-content-pack.mjs [path-to-pack]
 * Default pack path: ./_pack (not committed)
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");
const PACK_ROOT = path.resolve(ROOT, process.argv[2] || "_pack");

const LEVEL_MAP = { bas: "basic", int: "intermediate", adv: "advanced" };

const PART2_THEME = {
  basic: ["Yes/No", "What", "Where", "When", "Who", "Why", "How"],
  intermediate: ["Yes/No", "What", "Where", "When", "Who", "Why", "How"],
  advanced: [
    "Yes/No",
    "Future-tense Q",
    "Which",
    "Choice Q",
    "Tag questions",
    "Statements",
    "Indirect Q",
  ],
};

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, obj) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(obj, null, 2) + "\n");
}

function loadAnswerKeys() {
  const keys = {};
  for (const [packLevel, siteLevel] of Object.entries(LEVEL_MAP)) {
    const file = path.join(PACK_ROOT, "keys", `${packLevel}-answers.json`);
    if (fs.existsSync(file)) keys[siteLevel] = readJson(file).answers || {};
  }
  return keys;
}

function packPathForPractice(practiceId) {
  const prefix = practiceId.split("-")[0];
  const packLevel = prefix;
  return path.join(PACK_ROOT, "items", packLevel, `${practiceId}.json`);
}

function normalizeAccept(accept, keyFallback) {
  if (Array.isArray(accept) && accept.length) return String(accept[0]).trim();
  if (typeof accept === "string" && accept.trim()) return accept.trim();
  return keyFallback || null;
}

function letterChoices(n) {
  const letters = ["A", "B", "C", "D"].slice(0, n);
  return Object.fromEntries(letters.map((l) => [l, l]));
}

function choiceObjectFromPack(choices) {
  if (choices && typeof choices === "object" && !Array.isArray(choices)) {
    const out = {};
    for (const [k, v] of Object.entries(choices)) {
      if (v != null && String(v).trim() !== "") out[k] = String(v);
    }
    if (Object.keys(out).length) return out;
  }
  if (Array.isArray(choices) && choices.length) {
    return Object.fromEntries(choices.map((c) => [String(c), String(c)]));
  }
  return null;
}

function inferChoiceCount(practiceId, item, parsed) {
  const fromPack = choiceObjectFromPack(item.choices);
  if (fromPack) return Object.keys(fromPack).length;
  const acc = normalizeAccept(item.accept);
  if (acc === "D") return 4;
  if (practiceId.includes("-lc-p2-")) return 3;
  if (practiceId.includes("-lc-at-")) {
    if (acc === "D") return 4;
    const qNum = parseInt(String(item.label || "").replace(/\D/g, ""), 10);
    if (!Number.isNaN(qNum) && qNum >= 36) return 4;
    return 3;
  }
  if (item.audioOnly) return acc === "D" ? 4 : 3;
  return 4;
}

function resolveChoices(practiceId, item) {
  const fromPack = choiceObjectFromPack(item.choices);
  if (fromPack) return fromPack;
  const n = inferChoiceCount(practiceId, item);
  return letterChoices(n);
}

function mapPhoto(photo, levelId) {
  if (!photo) return undefined;
  const m = photo.match(/photos\/(?:bas|int|adv)\/([^/]+)\/(.+)$/);
  if (m) return `${levelId}/${m[1]}/${m[2]}`;
  return photo;
}

function itemLabel(label, index) {
  if (label) return String(label).replace(/^Q/i, "");
  return String(index + 1);
}

function sectionKeyFromPracticeId(practiceId) {
  const m = practiceId.match(/-(lc|rc)-(.+)$/);
  if (!m) return null;
  const tail = m[2];
  if (tail.startsWith("at-")) return `${m[1]}-at`;
  return tail;
}

function questionNumberFromItem(item, index) {
  const n = parseInt(String(item.label || "").replace(/\D/g, ""), 10);
  return Number.isNaN(n) ? index + 1 : n;
}

function lookupKeyAccept(practiceId, packPractice, item, index, answerKeys) {
  const levelId = LEVEL_MAP[practiceId.split("-")[0]];
  const sections = answerKeys[levelId];
  if (!sections) return null;
  const section = packPractice.section || sectionKeyFromPracticeId(practiceId);
  if (!section) return null;
  const bucket = sections[section];
  if (!bucket) return null;
  const q = questionNumberFromItem(item, index);
  if (practiceId.includes("-rc-at-")) {
    const bookQ = packPractice.bookQ && packPractice.bookQ[0];
    if (bookQ) return bucket[String(bookQ + index)] || bucket[String(q)] || null;
  }
  return bucket[String(q)] || null;
}

function introForPractice(practiceId, skill, subtitle) {
  if (skill === "lc") {
    if (practiceId.includes("-lc-p1-")) {
      return "Listen to each statement and choose the answer that best describes the picture.";
    }
    if (practiceId.includes("-lc-p2-")) {
      return `Listen to each question and choose the best response (${subtitle || "Part II"}).`;
    }
    if (practiceId.includes("-lc-p3-")) {
      return "Listen to the conversation or talk and choose the best answer.";
    }
    if (practiceId.includes("-lc-at-")) {
      return "Listening Actual Test — choose the best answer for each question.";
    }
  }
  if (skill === "rc") {
    if (practiceId.includes("-rc-at-")) {
      return "Reading Actual Test — choose the best answer for each question.";
    }
    if (practiceId.includes("-rc-p5-")) {
      return "Read the passage and choose the best answer.";
    }
    return "Choose the best answer to complete the sentence or question.";
  }
  return "";
}

function convertItem(item, index, practiceId, levelId, packPractice, answerKeys, sharedPassage) {
  const keyAccept = lookupKeyAccept(practiceId, packPractice, item, index, answerKeys);
  const accept = normalizeAccept(item.accept, keyAccept);
  const choices = resolveChoices(practiceId, item);
  const out = {
    id: `q${index + 1}`,
    label: itemLabel(item.label, index),
    type: "choice",
    choices,
  };

  if (item.stem && String(item.stem).trim()) {
    out.prompt = String(item.stem).trim();
  } else if (item.audioOnly || packPractice.section === "lc-at") {
    if (practiceId.includes("-lc-p1-")) {
      out.prompt = "Choose the best answer for this picture.";
    } else if (practiceId.includes("-lc-p2-") || practiceId.includes("-lc-at-")) {
      out.prompt = "Mark the best response to the question you hear.";
    }
  }

  if (accept) out.accept = accept;

  if (item.audioOnly || (practiceId.includes("-lc-at-") && !item.stem)) {
    out.audioOnly = true;
  }

  const photo = mapPhoto(item.photo, levelId);
  if (photo) out.photo = photo;

  if (index === 0 && sharedPassage) {
    out.passage = sharedPassage;
  }

  if (item.notes && String(item.notes).includes("proofread")) {
    out._note = String(item.notes);
  }

  return out;
}

function practiceIsStub(items) {
  if (!items.length) return true;
  return items.some((it) => !it.accept);
}

function updateCatalogSubtitles(catalog) {
  for (const track of catalog.tracks || []) {
    for (const p of track.practices || []) {
      const m = p.id.match(/-lc-p2-s(\d+)$/);
      if (m && PART2_THEME[p.level]) {
        const idx = parseInt(m[1], 10) - 1;
        if (PART2_THEME[p.level][idx]) p.subtitle = PART2_THEME[p.level][idx];
      }
      if (catalog.practiceIndex && catalog.practiceIndex[p.id]) {
        catalog.practiceIndex[p.id].subtitle = p.subtitle;
      }
    }
  }
}

function main() {
  if (!fs.existsSync(PACK_ROOT)) {
    console.error("Pack not found:", PACK_ROOT);
    process.exit(1);
  }

  const catalogPath = path.join(ROOT, "data/catalog.json");
  const catalog = readJson(catalogPath);
  const answerKeys = loadAnswerKeys();

  let imported = 0;
  let stubCount = 0;

  for (const [practiceId, meta] of Object.entries(catalog.practiceIndex || {})) {
    const packFile = packPathForPractice(practiceId);
    if (!fs.existsSync(packFile)) {
      console.warn("Missing pack file:", practiceId);
      continue;
    }
    const pack = readJson(packFile);
    const items = (pack.items || []).map((item, idx) =>
      convertItem(item, idx, practiceId, meta.level, pack, answerKeys, pack.passage || null)
    );

    const stub = practiceIsStub(items);
    if (stub) stubCount++;

    const practice = {
      practiceId,
      title: meta.title,
      subtitle: meta.subtitle || "",
      level: meta.level,
      skill: meta.skill,
      stub,
      audioRef: meta.audioRef || null,
      photoDir: meta.photoDir || null,
      introEn: introForPractice(practiceId, meta.skill, meta.subtitle),
      items,
    };

    if (meta.skill === "lc" && practiceId.includes("-lc-p2-")) {
      practice.timerMinutes = 12;
    }

    Object.keys(practice).forEach((k) => {
      if (practice[k] == null) delete practice[k];
    });

    writeJson(path.join(ROOT, meta.dataPath), practice);
    meta.stub = stub;
    imported++;
  }

  updateCatalogSubtitles(catalog);
  for (const track of catalog.tracks || []) {
    for (const p of track.practices || []) {
      const idx = catalog.practiceIndex[p.id];
      if (idx) p.stub = idx.stub;
    }
  }

  writeJson(catalogPath, catalog);
  console.log(`Imported ${imported} practices (${stubCount} still stub).`);
}

main();
