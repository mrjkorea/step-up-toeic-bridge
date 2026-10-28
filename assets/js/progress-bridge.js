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

  function ingestProgressRows(rows) {
    (rows || []).forEach(function (row) {
      var id = rowPracticeId(row);
      if (!id) return;
      var scoreMax = row.score_max != null ? row.score_max : row.scoreMax;
      var scoreValue = row.score_value != null ? row.score_value : row.scoreValue;
      var scorePct = row.score_pct != null ? row.score_pct : row.scorePct;
      if (scoreMax == null || scoreMax === "") return;
      if (scorePct == null && scoreValue != null && Number(scoreMax) > 0) {
        scorePct = Math.round((Number(scoreValue) / Number(scoreMax)) * 100);
      }
      cloudScores[id] = {
        practiceId: id,
        scoreValue: Number(scoreValue),
        scoreMax: Number(scoreMax),
        scorePct: scorePct,
        at: row.updated_at || row.updatedAt || row.local_date || row.localDate || "",
      };
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
    if (signedIn() && cloudScores[practiceId]) {
      return cloudScores[practiceId];
    }
    if (root.STEPUP_SCORES && root.STEPUP_SCORES.loadLocal) {
      return root.STEPUP_SCORES.loadLocal(practiceId);
    }
    return null;
  }

  function scorePctOf(practiceId) {
    var s = getScore(practiceId);
    if (!s || s.scoreMax == null || s.scoreMax === "") return null;
    if (s.scorePct != null && s.scorePct !== "") return Number(s.scorePct);
    if (s.scoreValue != null && Number(s.scoreMax) > 0) {
      return Math.round((Number(s.scoreValue) / Number(s.scoreMax)) * 100);
    }
    return null;
  }

  function isComplete(practiceId) {
    var pct = scorePctOf(practiceId);
    return pct != null && pct >= RETRY_PCT;
  }

  function mustRetry(practiceId) {
    var s = getScore(practiceId);
    if (!s || !s.scoreMax) return false;
    var pct = scorePctOf(practiceId);
    return pct != null && pct < RETRY_PCT;
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
    cloudScores[practiceId] = {
      practiceId: practiceId,
      scoreValue: payload.scoreValue,
      scoreMax: payload.scoreMax,
      scorePct: payload.scorePct,
      at: payload.at || new Date().toISOString(),
    };
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
