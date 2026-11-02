/**
 * Gate logic smoke test (UNLOCK_ALL off). Run: node scripts/test-teacher-unlock.mjs
 */
import fs from "fs";
import vm from "vm";

const code = fs
  .readFileSync("assets/js/progress-bridge.js", "utf8")
  .replace("var UNLOCK_ALL = true;", "var UNLOCK_ALL = false;");

const storage = {};
const root = {
  localStorage: {
    getItem(k) {
      return storage[k] ?? null;
    },
    setItem(k, v) {
      storage[k] = String(v);
    },
  },
  MRJ_AUTH: {
    student() {
      return "test-student";
    },
    savePack() {},
    loadPack() {
      return Promise.resolve({ ok: true, progress_json: "{}" });
    },
    loadProgressForApp() {
      return Promise.resolve({ ok: true, progress: [] });
    },
  },
  STEPUP_SCORES: null,
  addEventListener() {},
};

vm.createContext(root);
vm.runInContext(code, root);

const P = root.STEPUP_PROGRESS;

const practices = [
  { id: "a", group: "G1" },
  { id: "b", group: "G1" },
  { id: "c", group: "G2" },
];

let failed = 0;
function assert(cond, msg) {
  if (!cond) {
    console.error("FAIL:", msg);
    failed++;
  }
}

assert(P.isUnlocked(practices, "a") === true, "first practice always open");
assert(P.isUnlocked(practices, "b") === false, "b locked without progress");
assert(P.isGroupUnlocked(practices, "G2") === false, "G2 locked");

P.teacherUnlockFromHere(practices, "b", "track-1");

assert(P.isTeacherUnlocked("b"), "b teacher unlocked");
assert(P.isTeacherUnlocked("a"), "a unlocked via start-from-here cascade");
assert(P.isUnlocked(practices, "b") === true, "b open after teacher unlock");
assert(P.isGroupUnlocked(practices, "G1") === true, "G1 open when section unlocked");

P.teacherRelock("b");
assert(!P.isTeacherUnlocked("b"), "b relocked");
assert(P.isTeacherUnlocked("a"), "a still teacher-open after b relock");

if (failed) {
  process.exit(1);
}
console.log("OK: teacher unlock gate logic");
