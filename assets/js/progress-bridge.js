/* Cloud + local progress, resume target (MRJ_AUTH pack when signed in) */
(function (root) {
  "use strict";

  var PROGRAM = "step-up-toeic-bridge";
  var RETRY_PCT = 50;
  var PASS_PCT = 80;
  var LS_RESUME = "stepup.resume.v1";
  var cloudScores = {};
  var resumeTarget = null;
  var packLoaded = false;
  var packLoadStarted = false;
  var resumeDirty = false;
  var changeListeners = [];

  function student() {
    try {
      return root.MRJ_AUTH && root.MRJ_AUTH.student
        ? String(root.MRJ_AUTH.student() || "").trim()
        : "";
    } catch (e) {
      return "";
    }
  }

  function signedIn() {
    return !!student();
  }

  function notifyChange() {
    changeListeners.forEach(function (fn) {
      try {
        fn();
      } catch (e) {}
    });
  }

  function readLocalResume() {
    try {
      var raw = localStorage.getItem(LS_RESUME);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function writeLocalResume(entry) {
    try {
      localStorage.setItem(LS_RESUME, JSON.stringify(entry));
    } catch (e) {}
  }

  function rowPracticeId(row) {
    if (!row || typeof row !== "object") return "";
    return String(row.item_id || row.itemId || row.item || "").trim();
  }

  function pctFromRecord(rec) {
    if (root.STEPUP_SCORES && root.STEPUP_SCORES.pctFromRecord) {
      return root.STEPUP_SCORES.pctFromRecord(rec);
    }
    if (!rec) return null;
    if (rec.scorePct != null && rec.scorePct !== "") return Number(rec.scorePct);
    if (rec.scoreValue != null && Number(rec.scoreMax) > 0) {
      return Math.round((Number(rec.scoreValue) / Number(rec.scoreMax)) * 100);
    }
    return null;
  }

  function mergeScoreRecords(prev, attempt) {
    if (root.STEPUP_SCORES && root.STEPUP_SCORES.mergeScoreRecords) {
      return root.STEPUP_SCORES.mergeScoreRecords(prev, attempt);
    }
    return attempt;
  }

  function normalizeStored(rec) {
    if (!rec || rec.scoreMax == null || rec.scoreMax === "") return null;
    var pct = pctFromRecord(rec);
    var bestPct =
      rec.bestScorePct != null && rec.bestScorePct !== ""
        ? Number(rec.bestScorePct)
        : pct;
    return {
      practiceId: rec.practiceId,
      scoreValue: rec.scoreValue,
      scoreMax: Number(rec.scoreMax),
      scorePct: pct,
      at: rec.at || "",
      bestScoreValue:
        rec.bestScoreValue != null && rec.bestScoreValue !== ""
          ? rec.bestScoreValue
          : rec.scoreValue,
      bestScoreMax:
        rec.bestScoreMax != null && rec.bestScoreMax !== ""
          ? Number(rec.bestScoreMax)
          : Number(rec.scoreMax),
      bestScorePct: bestPct,
      bestAt: rec.bestAt || rec.at || "",
    };
  }

  function mergeStoredRecords(a, b) {
    var na = normalizeStored(a);
    var nb = normalizeStored(b);
    if (!na) return nb;
    if (!nb) return na;

    var latest = String(na.at || "") >= String(nb.at || "") ? na : nb;
    var bestPctA = na.bestScorePct;
    var bestPctB = nb.bestScorePct;
    var bestSource = na;
    if (bestPctB != null && (bestPctA == null || bestPctB > bestPctA)) {
      bestSource = nb;
    } else if (
      bestPctA != null &&
      bestPctB != null &&
      bestPctB === bestPctA &&
      String(nb.bestAt || nb.at || "") < String(na.bestAt || na.at || "")
    ) {
      bestSource = nb;
    }

    return {
      practiceId: na.practiceId || nb.practiceId,
      scoreValue: latest.scoreValue,
      scoreMax: latest.scoreMax,
      scorePct: latest.scorePct,
      at: latest.at,
      bestScoreValue: bestSource.bestScoreValue,
      bestScoreMax: bestSource.bestScoreMax,
      bestScorePct: bestSource.bestScorePct,
      bestAt: bestSource.bestAt,
    };
  }

  function rowToAttempt(row, id) {
    var scoreMax = row.score_max != null ? row.score_max : row.scoreMax;
    var scoreValue = row.score_value != null ? row.score_value : row.scoreValue;
    var scorePct = row.score_pct != null ? row.score_pct : row.scorePct;
    if (scoreMax == null || scoreMax === "") return null;
    if (scorePct == null && scoreValue != null && Number(scoreMax) > 0) {
      scorePct = Math.round((Number(scoreValue) / Number(scoreMax)) * 100);
    }
    return {
      practiceId: id,
      scoreValue: Number(scoreValue),
      scoreMax: Number(scoreMax),
      scorePct: scorePct,
      at: row.updated_at || row.updatedAt || row.local_date || row.localDate || "",
    };
  }

  function ingestProgressRows(rows) {
    (rows || []).forEach(function (row) {
      var id = rowPracticeId(row);
      if (!id) return;
      var attempt = rowToAttempt(row, id);
      if (!attempt) return;
      var prev = cloudScores[id];
      cloudScores[id] = mergeScoreRecords(prev, attempt);
    });
    notifyChange();
  }

  function applyPackJson(json) {
    if (!json) return;
    try {
      var pack = typeof json === "string" ? JSON.parse(json) : json;
      if (pack && pack.last && pack.last.practiceId) {
        resumeTarget = pack.last;
      }
    } catch (e) {}
  }

  function packPayload() {
    return JSON.stringify({
      v: 1,
      last: resumeTarget || readLocalResume() || null,
    });
  }

  function savePackToCloud() {
    if (!signedIn()) return;
    if (!packLoaded) {
      resumeDirty = true;
      return;
    }
    if (!root.MRJ_AUTH || typeof root.MRJ_AUTH.savePack !== "function") return;
    resumeDirty = false;
    root.MRJ_AUTH.savePack(PROGRAM, packPayload());
  }

  function loadCloudState() {
    if (!signedIn()) return Promise.resolve();
    if (packLoadStarted) return Promise.resolve();
    packLoadStarted = true;

    var chain = Promise.resolve();

    if (root.MRJ_AUTH && typeof root.MRJ_AUTH.loadProgressForApp === "function") {
      chain = chain.then(function () {
        return root.MRJ_AUTH.loadProgressForApp(PROGRAM).then(function (result) {
          if (result && result.ok && result.progress) {
            ingestProgressRows(result.progress);
          }
        });
      });
    }

    if (root.MRJ_AUTH && typeof root.MRJ_AUTH.loadPack === "function") {
      chain = chain.then(function () {
        return root.MRJ_AUTH.loadPack(PROGRAM).then(function (result) {
          if (result && result.ok) {
            packLoaded = true;
            applyPackJson(result.progress_json);
            if (resumeDirty) savePackToCloud();
            notifyChange();
          }
        });
      });
    }

    return chain;
  }

  function getScore(practiceId) {
    var local =
      root.STEPUP_SCORES && root.STEPUP_SCORES.loadLocal
        ? root.STEPUP_SCORES.loadLocal(practiceId)
        : null;
    var cloud = signedIn() ? cloudScores[practiceId] : null;
    if (local && cloud) return mergeStoredRecords(local, cloud);
    if (cloud) return normalizeStored(cloud);
    if (local) return normalizeStored(local);
    return null;
  }

  function bestScorePctOf(practiceId) {
    var s = getScore(practiceId);
    if (!s) return null;
    if (s.bestScorePct != null && s.bestScorePct !== "") return Number(s.bestScorePct);
    return pctFromRecord(s);
  }

  function scorePctOf(practiceId) {
    return bestScorePctOf(practiceId);
  }

  function isComplete(practiceId) {
    var pct = bestScorePctOf(practiceId);
    return pct != null && pct >= RETRY_PCT;
  }

  function mustRetry(practiceId) {
    var s = getScore(practiceId);
    if (!s || !s.scoreMax) return false;
    return !isComplete(practiceId);
  }

  function isUnlocked(practices, practiceId) {
    if (!practices || !practices.length) return true;
    var idx = -1;
    for (var i = 0; i < practices.length; i++) {
      if (practices[i].id === practiceId) {
        idx = i;
        break;
      }
    }
    if (idx <= 0) return true;
    return isComplete(practices[idx - 1].id);
  }

  function groupComplete(practices, groupName) {
    var any = false;
    var all = true;
    (practices || []).forEach(function (p) {
      if (p.group !== groupName) return;
      any = true;
      if (!isComplete(p.id)) all = false;
    });
    return any && all;
  }

  function isGroupUnlocked(practices, groupName) {
    if (!practices || !practices.length) return true;
    var groupOrder = [];
    var seen = {};
    practices.forEach(function (p) {
      if (!p.group || seen[p.group]) return;
      seen[p.group] = true;
      groupOrder.push(p.group);
    });
    var gi = groupOrder.indexOf(groupName);
    if (gi <= 0) return true;
    return groupComplete(practices, groupOrder[gi - 1]);
  }

  function getResume() {
    if (signedIn() && resumeTarget && resumeTarget.practiceId) {
      return resumeTarget;
    }
    return readLocalResume();
  }

  function sameResumeTarget(a, b) {
    if (!a || !b) return false;
    return (
      String(a.practiceId || "") === String(b.practiceId || "") &&
      String(a.trackId || "") === String(b.trackId || "")
    );
  }

  function touch(practiceId, trackId) {
    var prev =
      resumeTarget ||
      (signedIn() ? null : readLocalResume());
    var entry = {
      practiceId: practiceId,
      trackId: trackId || "",
      at: Date.now(),
    };
    var changed = !sameResumeTarget(prev, entry);
    writeLocalResume(entry);
    resumeTarget = entry;
    savePackToCloud();
    if (changed) notifyChange();
  }

  function onScorePersisted(practiceId, payload) {
    if (!signedIn()) return;
    var prev = cloudScores[practiceId];
    cloudScores[practiceId] = prev
      ? mergeStoredRecords(prev, payload)
      : normalizeStored(payload);
    notifyChange();
  }

  function onChange(fn) {
    if (typeof fn !== "function") return function () {};
    changeListeners.push(fn);
    return function () {
      changeListeners = changeListeners.filter(function (x) {
        return x !== fn;
      });
    };
  }

  root.addEventListener("mrj-auth-ready", function (ev) {
    packLoadStarted = false;
    if (ev && ev.detail && ev.detail.progress) {
      ingestProgressRows(ev.detail.progress);
    }
    loadCloudState();
  });

  root.STEPUP_PROGRESS = {
    PROGRAM: PROGRAM,
    RETRY_PCT: RETRY_PCT,
    PASS_PCT: PASS_PCT,
    getScore: getScore,
    scorePctOf: scorePctOf,
    bestScorePctOf: bestScorePctOf,
    isComplete: isComplete,
    mustRetry: mustRetry,
    isUnlocked: isUnlocked,
    isGroupUnlocked: isGroupUnlocked,
    groupComplete: groupComplete,
    getResume: getResume,
    touch: touch,
    onScorePersisted: onScorePersisted,
    refresh: loadCloudState,
    onChange: onChange,
  };
})(typeof window !== "undefined" ? window : globalThis);
