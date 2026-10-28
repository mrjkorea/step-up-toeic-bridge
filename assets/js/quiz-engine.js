/* Step Up TOEIC Bridge — grading (all item types) */
(function (root) {
  "use strict";

  function norm(s) {
    return String(s == null ? "" : s).trim().toLowerCase();
  }

  function acceptList(accept) {
    if (Array.isArray(accept)) return accept.map(String);
    if (accept == null) return [];
    return [String(accept)];
  }

  function itemType(item) {
    return String((item && item.type) || "choice").trim();
  }

  function isScoredItem(item) {
    if (!item || item.displayOnly) return false;
    if (item.scored === false) return false;
    if (item.blocked === true || item.blocked === "true") return false;
    return true;
  }

  function gradeChoice(item, value) {
    var val = String(value || "").trim();
    var ok = acceptList(item.accept);
    return ok.some(function (a) {
      return norm(a) === norm(val);
    });
  }

  function gradeText(item, value) {
    var val = norm(value);
    return acceptList(item.accept).some(function (a) {
      return norm(a) === val;
    });
  }

  function gradeMatch(item, links) {
    var pairs = item.pairs || [];
    if (!pairs.length) return false;
    links = links || {};
    for (var i = 0; i < pairs.length; i++) {
      var left = pairs[i].left;
      var right = pairs[i].right;
      if (norm(links[left]) !== norm(right)) return false;
    }
    return true;
  }

  function gradeSelfcheck(item, response) {
    response = response || {};
    if (item.allowHeard !== false && response.heard) return true;
    var targets = acceptList(item.accept);
    if (!targets.length && item.target) targets = acceptList(item.target);
    if (!targets.length && item.phrase) targets = acceptList(item.phrase);
    if (!targets.length) return false;
    return gradeText({ accept: targets }, response.value);
  }

  function gradeItem(item, response) {
    if (item.displayOnly || item.scored === false) return true;
    var type = itemType(item);
    if (type === "match") return gradeMatch(item, response && response.links);
    if (type === "choice" || type === "dropdown" || type === "tf") {
      return gradeChoice(item, response && response.value);
    }
    if (type === "text" || type === "typed" || type === "fill") {
      return gradeText(item, response && response.value);
    }
    if (type === "selfcheck" || type === "repeat" || type === "listen-repeat") {
      return gradeSelfcheck(item, response);
    }
    return false;
  }

  function gradePractice(practice, responses) {
    responses = responses || {};
    var items = (practice.items || []).filter(isScoredItem);
    var correct = 0;
    var detail = [];
    (practice.items || []).forEach(function (it) {
      if (!isScoredItem(it)) return;
      var ok = gradeItem(it, responses[it.id]);
      if (ok) correct++;
      detail.push({ id: it.id, correct: ok });
    });
    return {
      scoreValue: correct,
      scoreMax: items.length,
      scorePct: items.length ? Math.round((correct / items.length) * 100) : 0,
      detail: detail,
    };
  }

  root.STEPUP_QUIZ = {
    gradePractice: gradePractice,
    gradeItem: gradeItem,
    isScoredItem: isScoredItem,
  };
})(typeof window !== "undefined" ? window : globalThis);
