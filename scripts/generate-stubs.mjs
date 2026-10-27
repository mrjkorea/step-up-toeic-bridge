#!/usr/bin/env node
/**
 * Generates catalog metadata, stub practice JSON, audio manifest entries, and file paths.
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");

const LEVELS = [
  { id: "basic", prefix: "bas", label: "Basic" },
  { id: "intermediate", prefix: "int", label: "Intermediate" },
  { id: "advanced", prefix: "adv", label: "Advanced" },
];

const PART2_THEME = {
  basic: ["Yes/No", "What", "Where", "When", "Who", "Why", "How"],
  intermediate: ["Yes/No", "What", "Where", "When", "Who", "Why", "How"],
  advanced: ["Yes/No", "Future-tense Q", "Which", "Choice Q", "Tag questions", "Statements", "Indirect Q"],
};

const PART4_THEME = {
  basic: [
    "Kinds of sentences",
    "Sentence parts",
    "Nouns",
    "Verbs",
    "Pronouns",
    "Food",
    "School",
    "Clothes",
    "Hobbies",
  ],
  intermediate: [
    "Articles",
    "Modals",
    "Adjectives",
    "Adverbs",
    "Comparatives",
    "Jobs",
    "Illness / body",
    "Leisure",
    "House",
  ],
  advanced: [
    "To-inf / gerunds",
    "Participles / voice",
    "Agreement",
    "Conjunctions",
    "Prepositions",
    "Senses",
    "Body & feelings",
    "Conversation",
    "City & places",
  ],
};

const PART5_THEME = [
  "Notices",
  "Ads",
  "Instructions / info",
  "Letters & email",
  "Charts",
  "Memos",
  "Forms",
];

const AT_RANGES = [
  { suffix: "q01-10", label: "Questions 01–10", bookNote: "" },
  { suffix: "q11-20", label: "Questions 11–20", bookNote: "" },
  { suffix: "q21-30", label: "Questions 21–30", bookNote: "" },
  { suffix: "q31-40", label: "Questions 31–40", bookNote: "" },
  { suffix: "q41-50", label: "Questions 41–50", bookNote: "" },
];

const RC_AT_RANGES = AT_RANGES.map((r, i) => ({
  ...r,
  bookNote: `(book Q${51 + i * 10}–${60 + i * 10})`,
}));

function pad2(n) {
  return String(n).padStart(2, "0");
}

function ensureDir(d) {
  fs.mkdirSync(d, { recursive: true });
}

function writeJson(file, obj) {
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, JSON.stringify(obj, null, 2) + "\n");
}

function stubPractice(meta) {
  return {
    practiceId: meta.id,
    title: meta.title,
    subtitle: meta.subtitle || "",
    level: meta.level,
    skill: meta.skill,
    stub: true,
    audioRef: meta.audioRef || null,
    photoDir: meta.photoDir || null,
    items: [],
    _note: "Content placeholder — add items from the book answer key.",
  };
}

function buildLcPractices(level) {
  const { id: levelId, prefix } = level;
  const list = [];
  for (let s = 1; s <= 4; s++) {
    const id = `${prefix}-lc-p1-s${pad2(s)}`;
    list.push({
      id,
      level: levelId,
      skill: "lc",
      group: "Part I : Picture Description",
      title: `Part I · Section ${pad2(s)}`,
      subtitle: "Picture Description",
      audioRef: id,
      photoDir: `${levelId}/p1-s${pad2(s)}`,
      dataPath: `data/${levelId}/lc/${id}.json`,
    });
  }
  for (let s = 1; s <= 7; s++) {
    const id = `${prefix}-lc-p2-s${pad2(s)}`;
    list.push({
      id,
      level: levelId,
      skill: "lc",
      group: "Part II : Question and Response",
      title: `Part II · Section ${pad2(s)}`,
      subtitle: PART2_THEME[levelId][s - 1],
      audioRef: id,
      dataPath: `data/${levelId}/lc/${id}.json`,
    });
  }
  for (let s = 1; s <= 6; s++) {
    const id = `${prefix}-lc-p3-s${pad2(s)}`;
    list.push({
      id,
      level: levelId,
      skill: "lc",
      group: "Part III : Short Conversation and Talks",
      title: `Part III · Section ${pad2(s)}`,
      subtitle: "Conversations & talks",
      audioRef: id,
      dataPath: `data/${levelId}/lc/${id}.json`,
    });
  }
  for (const r of AT_RANGES) {
    const id = `${prefix}-lc-at-${r.suffix}`;
    list.push({
      id,
      level: levelId,
      skill: "lc",
      group: "LC Actual Test",
      title: `LC Actual Test · ${r.label}`,
      subtitle: "10 questions",
      audioRef: `${prefix}-lc-at`,
      dataPath: `data/${levelId}/lc/${id}.json`,
    });
  }
  return list;
}

function buildRcPractices(level) {
  const { id: levelId, prefix } = level;
  const list = [];
  for (let s = 1; s <= 9; s++) {
    const id = `${prefix}-rc-p4-s${pad2(s)}`;
    list.push({
      id,
      level: levelId,
      skill: "rc",
      group: "Part IV : Grammar and Words",
      title: `Part IV · Section ${pad2(s)}`,
      subtitle: PART4_THEME[levelId][s - 1],
      dataPath: `data/${levelId}/rc/${id}.json`,
    });
  }
  for (let s = 1; s <= 7; s++) {
    const id = `${prefix}-rc-p5-s${pad2(s)}`;
    list.push({
      id,
      level: levelId,
      skill: "rc",
      group: "Part V : Reading Comprehension",
      title: `Part V · Section ${pad2(s)}`,
      subtitle: PART5_THEME[s - 1],
      dataPath: `data/${levelId}/rc/${id}.json`,
    });
  }
  for (const r of RC_AT_RANGES) {
    const id = `${prefix}-rc-at-${r.suffix}`;
    list.push({
      id,
      level: levelId,
      skill: "rc",
      group: "RC Actual Test",
      title: `RC Actual Test · ${r.label}`,
      subtitle: `10 questions ${r.bookNote}`.trim(),
      dataPath: `data/${levelId}/rc/${id}.json`,
    });
  }
  return list;
}

/** Audio paths from AUDIO_MANIFEST (practiceId -> repo-relative paths under audio/) */
function audioManifestEntries() {
  const practices = {};
  for (const level of LEVELS) {
    const folder = level.id;
    const p = level.prefix;
    for (let s = 1; s <= 4; s++) {
      const id = `${p}-lc-p1-s${pad2(s)}`;
      practices[id] = { files: [`${folder}/p1-s${pad2(s)}.mp4`] };
    }
    for (let s = 1; s <= 7; s++) {
      const id = `${p}-lc-p2-s${pad2(s)}`;
      if (level.id === "intermediate" && s === 6) {
        practices[id] = { files: [`${folder}/p2-s06a.mp4`, `${folder}/p2-s06b.mp4`] };
      } else {
        practices[id] = { files: [`${folder}/p2-s${pad2(s)}.mp4`] };
      }
    }
    for (let s = 1; s <= 6; s++) {
      const id = `${p}-lc-p3-s${pad2(s)}`;
      practices[id] = { files: [`${folder}/p3-s${pad2(s)}.mp4`] };
    }
    const atId = `${p}-lc-at`;
    practices[atId] = { files: [`${folder}/actual-test.mp4`] };
  }
  return practices;
}

function main() {
  const allPractices = [];
  const tracks = [];
  for (const level of LEVELS) {
    const lc = buildLcPractices(level);
    const rc = buildRcPractices(level);
    allPractices.push(...lc, ...rc);
    tracks.push({
      trackId: `${level.id}-lc`,
      level: level.id,
      levelLabel: level.label,
      skill: "lc",
      skillLabel: "Listening",
      practices: lc,
    });
    tracks.push({
      trackId: `${level.id}-rc`,
      level: level.id,
      levelLabel: level.label,
      skill: "rc",
      skillLabel: "Reading",
      practices: rc,
    });
  }

  const catalog = {
    appName: "Step Up TOEIC Bridge",
    program: "step-up-toeic-bridge",
    version: 1,
    tracks,
    practiceIndex: Object.fromEntries(allPractices.map((p) => [p.id, p])),
  };

  writeJson(path.join(ROOT, "data/catalog.json"), catalog);

  for (const p of allPractices) {
    const file = path.join(ROOT, p.dataPath);
    writeJson(file, stubPractice(p));
  }

  const manifest = {
    version: 1,
    note: "practiceId or audioRef keys map to mp4 paths relative to audio/",
    practices: audioManifestEntries(),
  };
  writeJson(path.join(ROOT, "audio/manifest.json"), manifest);

  // Placeholder photos for Part I folders
  const photoSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
  <rect fill="#e8eef5" width="400" height="300"/>
  <text x="200" y="150" text-anchor="middle" fill="#5a6b7d" font-family="sans-serif" font-size="16">Photo placeholder</text>
</svg>`;
  for (const level of LEVELS) {
    for (let s = 1; s <= 4; s++) {
      const dir = path.join(ROOT, "assets/photos", level.id, `p1-s${pad2(s)}`);
      ensureDir(dir);
      fs.writeFileSync(path.join(dir, "placeholder.svg"), photoSvg);
    }
  }

  // Collect unique audio file paths
  const audioFiles = new Set();
  for (const entry of Object.values(manifest.practices)) {
    for (const f of entry.files) audioFiles.add(f);
  }

  const stubMp4 = path.join(ROOT, "scripts/.stub-silent.mp4");
  if (!fs.existsSync(stubMp4)) {
    execSync(
      `ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -f lavfi -i color=c=black:s=320x240:d=1 -shortest -c:v libx264 -t 1 -pix_fmt yuv420p "${stubMp4}"`,
      { stdio: "ignore" }
    );
  }
  for (const rel of audioFiles) {
    const dest = path.join(ROOT, "audio", rel);
    ensureDir(path.dirname(dest));
    if (!fs.existsSync(dest)) {
      fs.copyFileSync(stubMp4, dest);
    }
  }

  console.log(`Generated ${allPractices.length} practices, ${audioFiles.size} audio stubs.`);
}

main();
