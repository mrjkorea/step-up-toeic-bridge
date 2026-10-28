/* Local score persistence + MRJ_SCORES when signed in */
(function (root) {
  "use strict";

  var PROGRAM = "step-up-toeic-bridge";
  var LS_PREFIX = "stepup.score.";

  function loadLocal(practiceId) {
    try {
      var raw = localStorage.getItem(LS_PREFIX + practiceId);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function saveLocal(practiceId, payload) {
    try {
      localStorage.setItem(LS_PREFIX + practiceId, JSON.stringify(payload));
    } catch (e) {}
  }

  function pctFromRecord(rec) {
    if (!rec) return null;
    if (rec.scorePct != null && rec.scorePct !== "") return Number(rec.scorePct);
    if (rec.scoreValue != null && Number(rec.scoreMax) > 0) {
      return Math.round((Number(rec.scoreValue) / Number(rec.scoreMax)) * 100);
    }
    return null;
  }

  /** Merge a new attempt into stored progress; keeps latest attempt + best score (equal → keep earlier best). */
  function mergeScoreRecords(prev, attempt) {
    var practiceId = (attempt && attempt.practiceId) || (prev && prev.practiceId);
    var scoreValue = attempt.scoreValue;
    var scoreMax = attempt.scoreMax;
    var scorePct =
      typeof attempt.scorePct === "number"
        ? attempt.scorePct
        : pctFromRecord({ scoreValue: scoreValue, scoreMax: scoreMax });
    var at = attempt.at || new Date().toISOString();

    if (!prev || prev.scoreMax == null || prev.scoreMax === "") {
      return {
        practiceId: practiceId,
        scoreValue: scoreValue,
        scoreMax: scoreMax,
        scorePct: scorePct,
        at: at,
        bestScoreValue: scoreValue,
        bestScoreMax: scoreMax,
        bestScorePct: scorePct,
        bestAt: at,
      };
    }

    var prevBestPct =
      prev.bestScorePct != null && prev.bestScorePct !== ""
        ? Number(prev.bestScorePct)
        : pctFromRecord(prev);
    var out = {
      practiceId: practiceId || prev.practiceId,
      scoreValue: scoreValue,
      scoreMax: scoreMax,
      scorePct: scorePct,
      at: at,
      bestScoreValue:
        prev.bestScoreValue != null && prev.bestScoreValue !== ""
          ? prev.bestScoreValue
          : prev.scoreValue,
      bestScoreMax:
        prev.bestScoreMax != null && prev.bestScoreMax !== "" ? prev.bestScoreMax : prev.scoreMax,
      bestScorePct: prevBestPct,
      bestAt: prev.bestAt || prev.at,
    };

    if (scorePct != null && (prevBestPct == null || scorePct > prevBestPct)) {
      out.bestScoreValue = scoreValue;
      out.bestScoreMax = scoreMax;
      out.bestScorePct = scorePct;
      out.bestAt = at;
    }

    return out;
  }

  function persist(practice, result, durationSeconds) {
    var practiceId = practice.practiceId;
    var prev = loadLocal(practiceId);
    var payload = mergeScoreRecords(prev, {
      practiceId: practiceId,
      scoreValue: result.scoreValue,
      scoreMax: result.scoreMax,
      scorePct: result.scorePct,
      at: new Date().toISOString(),
    });
    saveLocal(practiceId, payload);

    if (root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.onScorePersisted) {
      root.STEPUP_PROGRESS.onScorePersisted(practiceId, payload);
    }

    if (root.MRJ_SCORES && typeof root.MRJ_SCORES.post === "function") {
      var levelLabel = practice.level || "";
      var skill = practice.skill === "lc" ? "Listening" : "Reading";
      root.MRJ_SCORES.post({
        program: PROGRAM,
        source: PROGRAM,
        appName: "Step Up TOEIC Bridge",
        bookTitle: levelLabel.charAt(0).toUpperCase() + levelLabel.slice(1) + " " + skill,
        unitTitle: practice.title || practiceId,
        itemId: practiceId,
        itemType: "practice_summary",
        scoreValue: result.scoreValue,
        scoreMax: result.scoreMax,
        scorePct: result.scorePct,
        completed: true,
        durationSeconds: durationSeconds || "",
        metadata: { subtitle: practice.subtitle || "" },
      });
    }
    return payload;
  }

  root.STEPUP_SCORES = {
    loadLocal: loadLocal,
    persist: persist,
    mergeScoreRecords: mergeScoreRecords,
    pctFromRecord: pctFromRecord,
  };
})(typeof window !== "undefined" ? window : globalThis);
