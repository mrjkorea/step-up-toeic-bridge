#!/usr/bin/env node
/**
 * LC Actual Test is shipped as five 10-question JSON files per level
 * ({pref}-lc-at-q01-10 … q41-50). To rebuild the legacy single 50-Q file:
 *   node scripts/merge-lc-at.mjs
 *
 * Content packs were sliced from live 50-Q LC Actual Test (Zap fixes preserved).
 */

console.log("LC Actual Test uses 5×10 chunk files under data/{basic,intermediate,advanced}/lc/.");
console.log("Merge back to one file: node scripts/merge-lc-at.mjs");
