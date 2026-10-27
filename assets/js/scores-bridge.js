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

  function persist(practice, result, durationSeconds) {
    var practiceId = practice.practiceId;
    var payload = {
      practiceId: practiceId,
      scoreValue: result.scoreValue,
      scoreMax: result.scoreMax,
      scorePct: result.scorePct,
      at: new Date().toISOString(),
    };
    saveLocal(practiceId, payload);

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
  };
})(typeof window !== "undefined" ? window : globalThis);
