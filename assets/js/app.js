/* Step Up TOEIC Bridge — shell (index, track list, practice) */
(function (root) {
  "use strict";

  var catalog = null;
  var catalogPromise = null;
  var startedAt = 0;
  var progressUnsub = null;

  var TRACK_CARDS = [
    { trackId: "basic-lc", title: "Basic", subtitle: "Listening (LC)", tone: "basic" },
    { trackId: "basic-rc", title: "Basic", subtitle: "Reading (RC)", tone: "basic" },
    { trackId: "intermediate-lc", title: "Intermediate", subtitle: "Listening (LC)", tone: "intermediate" },
    { trackId: "intermediate-rc", title: "Intermediate", subtitle: "Reading (RC)", tone: "intermediate" },
    { trackId: "advanced-lc", title: "Advanced", subtitle: "Listening (LC)", tone: "advanced" },
    { trackId: "advanced-rc", title: "Advanced", subtitle: "Reading (RC)", tone: "advanced" },
  ];

  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }

  function studentLabel() {
    if (root.MRJ_STUDENT) return String(root.MRJ_STUDENT);
    if (root.MRJ_AUTH && root.MRJ_AUTH.student) {
      return String(root.MRJ_AUTH.student() || "");
    }
    return "";
  }

  function loadCatalog() {
    if (catalog) return Promise.resolve(catalog);
    if (catalogPromise) return catalogPromise;
    catalogPromise = fetch(root.stepupUrl("data/catalog.json"), { cache: "no-cache" })
      .then(function (r) {
        if (!r.ok) throw new Error("catalog");
        return r.json();
      })
      .then(function (c) {
        catalog = c;
        return c;
      });
    return catalogPromise;
  }

  function parseRoute() {
    var hash = (root.location.hash || "#/").replace(/^#/, "");
    var parts = hash.split("/").filter(Boolean);
    if (!parts.length || parts[0] === "") return { view: "home" };
    if (parts[0] === "track" && parts[1]) return { view: "track", trackId: parts[1] };
    if (parts[0] === "practice" && parts[1]) return { view: "practice", practiceId: parts[1] };
    return { view: "home" };
  }

  function navigate(hash) {
    root.location.hash = hash;
  }

  function renderTopbar(title, backHash) {
    var bar = el("header", "topbar");
    if (backHash) {
      var back = el("a", "back-link", "← Back");
      back.href = backHash;
      bar.appendChild(back);
    }
    var brand = el("div", "brand", title);
    bar.appendChild(brand);
    var name = studentLabel();
    if (name) {
      var pill = el("span", "student-pill", name);
      bar.appendChild(pill);
    }
    return bar;
  }

  function scoreBadgeHtml(practiceId) {
    var saved =
      root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.getScore
        ? root.STEPUP_PROGRESS.getScore(practiceId)
        : root.STEPUP_SCORES && root.STEPUP_SCORES.loadLocal
          ? root.STEPUP_SCORES.loadLocal(practiceId)
          : null;
    if (!saved || !saved.scoreMax) return "";
    return (
      '<span class="score-pill">' +
      saved.scoreValue +
      "/" +
      saved.scoreMax +
      " (" +
      saved.scorePct +
      "%)</span>"
    );
  }

  function doneMarkHtml(practiceId) {
    var complete =
      root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.isComplete
        ? root.STEPUP_PROGRESS.isComplete(practiceId)
        : false;
    if (!complete) return "";
    return '<span class="badge-done" aria-label="Completed">✓</span>';
  }

  function resumeControl() {
    var resume =
      root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.getResume
        ? root.STEPUP_PROGRESS.getResume()
        : null;
    if (!resume || !resume.practiceId) return null;
    var wrap = el("div", "resume-bar");
    var btn = el("a", "btn-resume", "Continue where you left off");
    btn.href = "#/practice/" + resume.practiceId;
    wrap.appendChild(btn);
    return wrap;
  }

  function renderHome(app) {
    app.innerHTML = "";
    app.appendChild(renderTopbar("Step Up TOEIC Bridge"));
    var resume = resumeControl();
    if (resume) app.appendChild(resume);
    var intro = el(
      "p",
      "lead",
      "Zap-style practices for YBM Step Up TOEIC Bridge — Basic, Intermediate, and Advanced."
    );
    app.appendChild(intro);
    var grid = el("div", "card-grid");
    TRACK_CARDS.forEach(function (card) {
      var a = el("a", "track-card track-card--" + card.tone);
      a.href = "#/track/" + card.trackId;
      a.innerHTML =
        '<span class="track-card__level">' +
        card.title +
        '</span><span class="track-card__skill">' +
        card.subtitle +
        "</span>";
      grid.appendChild(a);
    });
    app.appendChild(grid);
    var note = el(
      "p",
      "footnote",
      "Practice content from YBM Step Up TOEIC Bridge answer keys; section audio plays from committed Drive MP4s."
    );
    app.appendChild(note);
  }

  function renderTrack(app, trackId) {
    loadCatalog().then(function (c) {
      var track = (c.tracks || []).find(function (t) {
        return t.trackId === trackId;
      });
      if (!track) {
        app.innerHTML = "<p>Track not found.</p>";
        return;
      }
      app.innerHTML = "";
      app.appendChild(renderTopbar(track.levelLabel + " · " + track.skillLabel, "#/"));
      var resume = resumeControl();
      if (resume) app.appendChild(resume);
      if (track.skill === "lc") {
        var audioNote = el(
          "p",
          "track-note",
          "Section audio plays inside each practice. E-book AUDIO leaves are not quizzes."
        );
        app.appendChild(audioNote);
      }
      var groups = {};
      (track.practices || []).forEach(function (p) {
        groups[p.group] = groups[p.group] || [];
        groups[p.group].push(p);
      });
      Object.keys(groups).forEach(function (groupName) {
        var section = el("section", "practice-group");
        section.appendChild(el("h2", "group-title", groupName));
        var list = el("div", "practice-list");
        groups[groupName].forEach(function (p) {
          var complete =
            root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.isComplete
              ? root.STEPUP_PROGRESS.isComplete(p.id)
              : false;
          var a = el(
            "a",
            "practice-card" +
              (p.stub === false ? " practice-card--live" : "") +
              (complete ? " practice-card--done" : "")
          );
          a.href = "#/practice/" + p.id;
          var sub = p.subtitle ? '<span class="practice-card__sub">' + p.subtitle + "</span>" : "";
          var stub =
            p.stub === false
              ? '<span class="badge-live">ready</span>'
              : '<span class="badge-stub">stub</span>';
          a.innerHTML =
            doneMarkHtml(p.id) +
            '<span class="practice-card__title">' +
            p.title +
            "</span>" +
            sub +
            stub +
            scoreBadgeHtml(p.id);
          list.appendChild(a);
        });
        section.appendChild(list);
        app.appendChild(section);
      });
    });
  }

  function renderChoiceItem(item, responses) {
    var card = el("article", "q-card");
    var label = el("div", "q-label", "Q" + (item.label || item.id));
    card.appendChild(label);
    if (item.photo) {
      var photoWrap = el("div", "q-photo");
      var img = document.createElement("img");
      img.alt = "Picture for question " + (item.label || item.id);
      img.src = root.stepupUrl("assets/photos/" + item.photo);
      img.loading = "lazy";
      photoWrap.appendChild(img);
      card.appendChild(photoWrap);
    }
    if (item.prompt) card.appendChild(el("p", "q-prompt", item.prompt));
    else if (item.stem) card.appendChild(el("p", "q-prompt", item.stem));
    if (item.passageHead) card.appendChild(el("p", "q-passage-head", item.passageHead));
    if (item.passage) card.appendChild(el("div", "q-passage", item.passage));
    else if (item.passageNote) card.appendChild(el("p", "q-passage-note", item.passageNote));
    var fieldset = el("fieldset", "q-choices");
    fieldset.setAttribute("aria-label", "Question " + item.label);
    var choices = item.choices || {};
    var keys = Object.keys(choices).sort();
    var current = responses[item.id] && responses[item.id].value;
    keys.forEach(function (k) {
      var id = item.id + "_" + k;
      var row = el("label", "choice-row");
      var text = choices[k];
      var letterOnly = text === k;
      row.innerHTML =
        '<input type="radio" name="' +
        item.id +
        '" value="' +
        k +
        '" id="' +
        id +
        '"' +
        (current === k ? " checked" : "") +
        ' /> <span class="choice-key">' +
        k +
        "</span>" +
        (letterOnly ? "" : ' <span class="choice-text">' + text + "</span>");
      fieldset.appendChild(row);
    });
    card.appendChild(fieldset);
    card.dataset.itemId = item.id;
    return card;
  }

  function renderMatchItem(item, responses) {
    var card = el("article", "q-card q-card--match");
    card.appendChild(el("div", "q-label", "Q" + (item.label || item.id)));
    if (item.prompt) card.appendChild(el("p", "q-prompt", item.prompt));
    var links = (responses[item.id] && responses[item.id].links) || {};
    var rights = (item.options && item.options.right) || [];
    (item.pairs || []).forEach(function (pair, idx) {
      var row = el("div", "match-row");
      row.innerHTML = '<span class="match-left">' + pair.left + "</span>";
      var sel = document.createElement("select");
      sel.name = item.id + "_m" + idx;
      sel.innerHTML = '<option value="">— choose —</option>';
      rights.forEach(function (r) {
        var opt = document.createElement("option");
        opt.value = r;
        opt.textContent = r;
        if (links[pair.left] === r) opt.selected = true;
        sel.appendChild(opt);
      });
      sel.addEventListener("change", function () {
        links[pair.left] = sel.value;
      });
      row.appendChild(sel);
      card.appendChild(row);
    });
    card.dataset.itemId = item.id;
    card.dataset.matchId = item.id;
    return card;
  }

  function collectResponses(form, practice) {
    var responses = {};
    (practice.items || []).forEach(function (item) {
      if (item.displayOnly) return;
      if (item.type === "match") {
        var links = {};
        var card = form.querySelector('[data-match-id="' + item.id + '"]');
        if (card) {
          card.querySelectorAll("select").forEach(function (sel, idx) {
            var left = item.pairs[idx].left;
            links[left] = sel.value;
          });
        }
        responses[item.id] = { links: links };
      } else {
        var picked = form.querySelector('input[name="' + item.id + '"]:checked');
        responses[item.id] = { value: picked ? picked.value : "" };
      }
    });
    return responses;
  }

  function renderPractice(app, practiceId) {
    loadCatalog().then(function (c) {
      var meta = c.practiceIndex && c.practiceIndex[practiceId];
      if (!meta) {
        app.innerHTML = "<p>Practice not found.</p>";
        return;
      }
      var trackId = meta.level + "-" + meta.skill;
      if (root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.touch) {
        root.STEPUP_PROGRESS.touch(practiceId, trackId);
      }
      fetch(root.stepupUrl(meta.dataPath), { cache: "no-cache" })
        .then(function (r) {
          return r.json();
        })
        .then(function (practice) {
          startedAt = Date.now();
          app.innerHTML = "";
          var title = practice.title || meta.title;
          var sub = practice.subtitle || meta.subtitle;
          app.appendChild(renderTopbar(title, "#/track/" + trackId));
          if (sub) app.appendChild(el("p", "practice-subtitle", sub));
          if (practice.introEn) app.appendChild(el("p", "practice-intro", practice.introEn));

          if (practice.skill === "lc" || meta.skill === "lc") {
            var audioBox = el("div", "audio-panel");
            app.appendChild(audioBox);
            if (root.STEPUP_AUDIO) {
              root.STEPUP_AUDIO.mount(audioBox, practice.audioRef || practiceId);
            }
          }

          var form = el("form", "practice-form");
          form.addEventListener("submit", function (e) {
            e.preventDefault();
          });

          var responses = {};
          var items = practice.items || [];
          if (!items.length && practice.stub) {
            form.appendChild(
              el(
                "p",
                "stub-msg",
                "This practice is a navigation stub. Content JSON is ready under <code>" +
                  meta.dataPath +
                  "</code>."
              )
            );
          } else {
            items.forEach(function (item) {
              if (item.type === "match") form.appendChild(renderMatchItem(item, responses));
              else form.appendChild(renderChoiceItem(item, responses));
            });
          }

          var actions = el("div", "practice-actions");
          var checkBtn = el("button", "btn-primary", "Check answers");
          checkBtn.type = "button";
          var resultBox = el("div", "result-box", "");
          checkBtn.addEventListener("click", function () {
            var resp = collectResponses(form, practice);
            var result = root.STEPUP_QUIZ.gradePractice(practice, resp);
            var duration = Math.round((Date.now() - startedAt) / 1000);
            root.STEPUP_SCORES.persist(practice, result, duration);
            resultBox.innerHTML =
              "<strong>Score: " +
              result.scoreValue +
              " / " +
              result.scoreMax +
              " (" +
              result.scorePct +
              "%)</strong>";
            resultBox.className = "result-box result-box--show";
            var byId = {};
            result.detail.forEach(function (d) {
              byId[d.id] = d;
            });
            form.querySelectorAll(".q-card").forEach(function (card) {
              var id = card.dataset.itemId;
              var graded = byId[id];
              if (!graded) return;
              card.classList.toggle("q-card--correct", graded.correct);
              card.classList.toggle("q-card--wrong", !graded.correct);
            });
          });
          actions.appendChild(checkBtn);
          form.appendChild(actions);
          form.appendChild(resultBox);
          app.appendChild(form);
        })
        .catch(function () {
          app.innerHTML = "<p>Could not load practice data.</p>";
        });
    });
  }

  function render() {
    var app = document.getElementById("stepup-app");
    if (!app) return;
    var route = parseRoute();
    if (route.view === "home") renderHome(app);
    else if (route.view === "track") renderTrack(app, route.trackId);
    else if (route.view === "practice") renderPractice(app, route.practiceId);
    else renderHome(app);
  }

  function bindProgressRefresh() {
    if (progressUnsub) progressUnsub();
    if (root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.onChange) {
      progressUnsub = root.STEPUP_PROGRESS.onChange(function () {
        render();
      });
    }
  }

  root.addEventListener("hashchange", render);
  root.addEventListener("mrj-auth-ready", function () {
    if (root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.refresh) {
      root.STEPUP_PROGRESS.refresh().then(render);
    } else {
      render();
    }
  });
  root.addEventListener("DOMContentLoaded", function () {
    if (!root.location.hash) root.location.hash = "#/";
    bindProgressRefresh();
    render();
    if (root.MRJ_SCORES && root.MRJ_SCORES.flush) root.MRJ_SCORES.flush();
  });
})(window);
