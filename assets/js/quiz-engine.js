/* Step Up TOEIC Bridge — grading (choice + match) */
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

  function gradeChoice(item, value) {
    var val = String(value || "").trim();
    var ok = acceptList(item.accept);
    return ok.some(function (a) {
      return norm(a) === norm(val);
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

  function gradeItem(item, response) {
    if (item.displayOnly) return true;
    var type = item.type || "choice";
    if (type === "match") return gradeMatch(item, response && response.links);
    if (type === "choice" || type === "dropdown") return gradeChoice(item, response && response.value);
    if (type === "text") {
      var val = norm(response && response.value);
      return acceptList(item.accept).some(function (a) {
        return norm(a) === val;
      });
    }
    return false;
  }

  function gradePractice(practice, responses) {
    responses = responses || {};
    var items = (practice.items || []).filter(function (it) {
      return !it.displayOnly;
    });
    var correct = 0;
    var detail = [];
    items.forEach(function (it) {
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
  };
})(typeof window !== "undefined" ? window : globalThis);
