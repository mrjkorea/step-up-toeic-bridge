/* Step Up TOEIC Bridge — shell (index, track list, practice) */
(function (root) {
  "use strict";

  var catalog = null;
  var catalogPromise = null;
  var startedAt = 0;
  var progressUnsub = null;
  var practiceTimerId = null;

  function clearPracticeTimer() {
    if (practiceTimerId != null) {
      clearInterval(practiceTimerId);
      practiceTimerId = null;
    }
  }

  function formatTimer(secs) {
    var n = Math.max(0, Math.floor(secs));
    var m = Math.floor(n / 60);
    var s = n % 60;
    return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
  }

  function secondsPerPlayableItem(skill) {
    return skill === "lc" ? 60 : 75;
  }

  var TRACK_CARDS = [
    { trackId: "basic-lc", title: "Basic", subtitle: "Listening (LC)", tone: "basic" },
    { trackId: "basic-rc", title: "Basic", subtitle: "Reading (RC)", tone: "basic" },
    { trackId: "intermediate-lc", title: "Intermediate", subtitle: "Listening (LC)", tone: "intermediate" },
    { trackId: "intermediate-rc", title: "Intermediate", subtitle: "Reading (RC)", tone: "intermediate" },
    { trackId: "advanced-lc", title: "Advanced", subtitle: "Listening (LC)", tone: "advanced" },
    { trackId: "advanced-rc", title: "Advanced", subtitle: "Reading (RC)", tone: "advanced" },
  ];

  var BOOK_LEVELS = [
    { level: "basic", title: "Basic", tone: "basic" },
    { level: "intermediate", title: "Intermediate", tone: "intermediate" },
    { level: "advanced", title: "Advanced", tone: "advanced" },
  ];

  function retryPct() {
    if (root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.RETRY_PCT != null) {
      return root.STEPUP_PROGRESS.RETRY_PCT;
    }
    if (root.STEPUP_QUIZ && root.STEPUP_QUIZ.RETRY_PCT != null) {
      return root.STEPUP_QUIZ.RETRY_PCT;
    }
    return 50;
  }

  function practiceComplete(practiceId) {
    return root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.isComplete
      ? root.STEPUP_PROGRESS.isComplete(practiceId)
      : false;
  }

  function practiceMustRetry(practiceId) {
    return root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.mustRetry
      ? root.STEPUP_PROGRESS.mustRetry(practiceId)
      : false;
  }

  function practiceUnlocked(practices, practiceId) {
    if (!practices || !practices.length) return true;
    if (root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.isUnlocked) {
      return root.STEPUP_PROGRESS.isUnlocked(practices, practiceId);
    }
    return true;
  }

  function groupUnlocked(practices, groupName) {
    if (root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.isGroupUnlocked) {
      return root.STEPUP_PROGRESS.isGroupUnlocked(practices, groupName);
    }
    return true;
  }

  function orderedGroups(practices) {
    var groups = [];
    var seen = {};
    (practices || []).forEach(function (p) {
      var g = p.group || "Practice";
      if (seen[g]) return;
      seen[g] = true;
      groups.push(g);
    });
    return groups;
  }

  function groupProgress(practices, groupName) {
    var total = 0;
    var done = 0;
    (practices || []).forEach(function (p) {
      if (p.group !== groupName) return;
      total++;
      if (practiceComplete(p.id)) done++;
    });
    return { done: done, total: total };
  }

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
    catalogPromise = fetch(root.stepupUrl("data/catalog.json?v=3"), { cache: "no-cache" })
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
    if (parts[0] === "book" && parts[1]) return { view: "book", level: parts[1] };
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

  function appendResumeBar(app, catalog) {
    var resume =
      root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.getResume
        ? root.STEPUP_PROGRESS.getResume()
        : null;
    if (!resume || !resume.practiceId || !catalog) return;
    var meta = catalog.practiceIndex && catalog.practiceIndex[resume.practiceId];
    if (!meta) return;
    var trackId = meta.level + "-" + meta.skill;
    var track = (catalog.tracks || []).find(function (t) {
      return t.trackId === trackId;
    });
    if (!track || !practiceUnlocked(track.practices, resume.practiceId)) return;
    var wrap = el("div", "resume-bar");
    var btn = el("a", "btn-resume", "Continue where you left off");
    btn.href = "#/practice/" + resume.practiceId;
    wrap.appendChild(btn);
    app.appendChild(wrap);
  }

  function renderHome(app) {
    loadCatalog().then(function (c) {
      app.innerHTML = "";
      app.appendChild(renderTopbar("Step Up TOEIC Bridge"));
      appendResumeBar(app, c);
      var intro = el(
        "p",
        "lead",
        "Zap-style practices for YBM Step Up TOEIC Bridge — Basic, Intermediate, and Advanced."
      );
      app.appendChild(intro);
      var grid = el("div", "card-grid");
      BOOK_LEVELS.forEach(function (book) {
        var a = el("a", "track-card track-card--" + book.tone);
        a.href = "#/book/" + book.level;
        a.innerHTML =
          '<span class="track-card__level">' +
          book.title +
          '</span><span class="track-card__skill">Listening + Reading map</span>';
        grid.appendChild(a);
      });
      app.appendChild(grid);
      var note = el(
        "p",
        "footnote",
        "Finish each section at 50% or higher to unlock the next. Practice content from YBM Step Up TOEIC Bridge answer keys; section audio plays from committed Drive MP4s."
      );
      app.appendChild(note);
    });
  }

  function buildPracticeCard(p, practices, trackId) {
    var complete = practiceComplete(p.id);
    var retry = practiceMustRetry(p.id);
    var unlocked = practiceUnlocked(practices, p.id);
    var cls =
      "practice-card" +
      (p.stub === false ? " practice-card--live" : "") +
      (complete ? " practice-card--done" : "") +
      (retry ? " practice-card--retry" : "") +
      (!unlocked ? " practice-card--locked" : "");
    var sub = p.subtitle ? '<span class="practice-card__sub">' + p.subtitle + "</span>" : "";
    var stub =
      p.stub === false
        ? '<span class="badge-live">ready</span>'
        : '<span class="badge-stub">stub</span>';
    var retryTag = retry ? '<span class="badge-retry">Try again</span>' : "";
    var lockTag = !unlocked ? '<span class="badge-lock" aria-hidden="true">🔒</span>' : "";
    var inner =
      lockTag +
      doneMarkHtml(p.id) +
      '<span class="practice-card__title">' +
      p.title +
      "</span>" +
      sub +
      retryTag +
      stub +
      scoreBadgeHtml(p.id);
    if (!unlocked) {
      var row = el("div", cls);
      row.innerHTML = inner;
      row.setAttribute("aria-disabled", "true");
      row.title = "Finish the previous section at " + retryPct() + "% or higher to unlock.";
      return row;
    }
    var a = el("a", cls);
    a.href = "#/practice/" + p.id;
    a.innerHTML = inner;
    return a;
  }

  function renderTrackMap(track, container) {
    var practices = track.practices || [];
    var groups = {};
    practices.forEach(function (p) {
      groups[p.group] = groups[p.group] || [];
      groups[p.group].push(p);
    });
    orderedGroups(practices).forEach(function (groupName) {
      var prog = groupProgress(practices, groupName);
      var gOpen = groupUnlocked(practices, groupName);
      var gDone = prog.total > 0 && prog.done === prog.total;
      var section = el(
        "section",
        "practice-group map-group" +
          (gDone ? " map-group--done" : "") +
          (!gOpen ? " map-group--locked" : " map-group--open")
      );
      var head = el("div", "map-group__head");
      head.appendChild(el("h2", "group-title", groupName));
      var stat = el(
        "span",
        "map-group__stat",
        prog.done + " / " + prog.total + " finished (≥" + retryPct() + "%)"
      );
      head.appendChild(stat);
      if (!gOpen) {
        head.appendChild(el("span", "map-group__lock-note", "Locked — finish the previous part first"));
      }
      section.appendChild(head);
      var list = el("div", "practice-list");
      (groups[groupName] || []).forEach(function (p) {
        list.appendChild(buildPracticeCard(p, practices, track.trackId));
      });
      section.appendChild(list);
      container.appendChild(section);
    });
  }

  function renderBook(app, level) {
    loadCatalog().then(function (c) {
      var bookMeta = BOOK_LEVELS.find(function (b) {
        return b.level === level;
      });
      if (!bookMeta) {
        app.innerHTML = "<p>Book not found.</p>";
        return;
      }
      var tracks = (c.tracks || []).filter(function (t) {
        return t.level === level;
      });
      app.innerHTML = "";
      app.appendChild(renderTopbar(bookMeta.title + " · Step Up", "#/"));
      appendResumeBar(app, c);
      var intro = el(
        "p",
        "lead",
        "Course map — Listening and Reading. Each step unlocks after you score at least " +
          retryPct() +
          "% on the previous exercise."
      );
      app.appendChild(intro);
      tracks.forEach(function (track) {
        var block = el("section", "book-skill-map");
        var head = el("div", "book-skill-map__head");
        head.appendChild(el("h2", "book-skill-title", track.skillLabel));
        var open = el("a", "book-skill-link", "Open " + track.skillLabel + " track →");
        open.href = "#/track/" + track.trackId;
        head.appendChild(open);
        block.appendChild(head);
        renderTrackMap(track, block);
        app.appendChild(block);
      });
    });
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
      app.appendChild(
        renderTopbar(track.levelLabel + " · " + track.skillLabel, "#/book/" + track.level)
      );
      appendResumeBar(app, c);
      if (track.skill === "lc") {
        var audioNote = el(
          "p",
          "track-note",
          "Section audio plays inside each practice. E-book AUDIO leaves are not quizzes."
        );
        app.appendChild(audioNote);
      }
      var mapIntro = el(
        "p",
        "track-map-note",
        "Green checkmarks mean ≥" + retryPct() + "%. Locked steps need the previous exercise finished first."
      );
      app.appendChild(mapIntro);
      var mapWrap = el("div", "track-map");
      renderTrackMap(track, mapWrap);
      app.appendChild(mapWrap);
    });
  }

  function normalizePhotoRef(ref) {
    var s = String(ref).trim();
    if (!s) return s;
    var parts = s.split("/");
    var base = parts[parts.length - 1];
    if (/^page-.+\.png$/i.test(base)) {
      parts[parts.length - 1] = base.replace(/\.png$/i, ".jpg");
      return parts.join("/");
    }
    return s;
  }

  function isContentDebug() {
    var h = root.location.hash || "";
    var q = root.location.search || "";
    return /(?:^|[?&])debug=1(?:&|$)/.test(q) || h.indexOf("debug=1") >= 0;
  }

  function isBlockedItem(item) {
    if (!item) return false;
    var b = item.blocked;
    if (b === false || b == null || b === "") return false;
    return true;
  }

  function isPlayableItem(item) {
    if (!item) return false;
    if (isBlockedItem(item)) return isContentDebug();
    return true;
  }

  function isForbiddenMediaRef(ref) {
    if (!ref) return false;
    var s = String(ref).trim();
    if (!s) return false;
    if (/page-/i.test(s) || /rc-pages/i.test(s)) return true;
    if (/bookPages/i.test(s)) return true;
    return false;
  }

  function isAllowedStudentPhoto(ref) {
    if (!ref || isForbiddenMediaRef(ref)) return false;
    var s = normalizePhotoRef(String(ref).trim());
    if (!s || /^https?:\/\//i.test(s)) return false;
    if (/page-/i.test(s) || /rc-pages/i.test(s)) return false;
    if (/^[^/]+\/at\/q\d+\.png$/i.test(s)) return true;
    if (/^[^/]+\/p1-s\d\d\/q0[1-6]\.png$/i.test(s)) return true;
    if (/^[^/]+\/p1-s\d\d\/(wu1|wu2|lp1|lp2)\.jpe?g$/i.test(s)) return true;
    return false;
  }

  function resolvePhotoUrl(ref) {
    if (!ref) return "";
    var s = normalizePhotoRef(String(ref).trim());
    if (!s) return "";
    if (/^https?:\/\//i.test(s)) return s;
    if (s.indexOf("assets/") === 0) return root.stepupUrl(s);
    return root.stepupUrl("assets/photos/" + s);
  }

  function attachPhotoFallback(img, url) {
    img.src = url;
    img.onerror = function () {
      if (img.dataset.swapped) return;
      img.dataset.swapped = "1";
      img.src = /\.png$/i.test(url)
        ? url.replace(/\.png$/i, ".jpg")
        : url.replace(/\.jpe?g$/i, ".png");
    };
  }

  function passageImageRef(item, practice) {
    if (item.passageImage) return item.passageImage;
    if (item.passagePage == null || item.passagePage === "") return null;
    var page = String(item.passagePage).trim();
    if (practice && practice.photoDir) {
      var base = String(practice.photoDir).replace(/\/$/, "");
      if (/\.(png|jpe?g|webp|svg)$/i.test(page)) return base + "/" + page;
      return base + "/" + page + ".png";
    }
    var level = (practice && practice.level) || "basic";
    if (/\.(png|jpe?g|webp|svg)$/i.test(page)) return level + "/rc/" + page;
    return level + "/rc/" + page + ".png";
  }

  function itemPageImageRef(item) {
    if (item.pageImage) return item.pageImage;
    if (item.photos) {
      if (typeof item.photos === "string") return item.photos;
      if (Array.isArray(item.photos) && item.photos.length) return item.photos[0];
    }
    return null;
  }

  function appendPhotoBlock(card, ref, altText) {
    if (!isAllowedStudentPhoto(ref)) return;
    var url = resolvePhotoUrl(ref);
    if (!url) return;
    var photoWrap = el("div", "q-photo");
    var img = document.createElement("img");
    img.alt = altText || "Picture for this question";
    img.loading = "lazy";
    attachPhotoFallback(img, url);
    photoWrap.appendChild(img);
    card.appendChild(photoWrap);
  }

  function appendPassageBlock(card, item, practice, passageShown) {
    var head = item.passageHead ? String(item.passageHead) : "";
    var bodyKey = item.passage ? "txt:" + item.passage : "";
    var passageKey = (head ? "h:" + head + "|" : "") + bodyKey;
    if (passageKey && passageShown[passageKey]) return;
    if (head) card.appendChild(el("p", "q-passage-head", head));
    if (item.passage) {
      card.appendChild(el("div", "q-passage", item.passage));
    }
    if (passageKey) passageShown[passageKey] = true;
  }

  function formatItemLabel(item) {
    if (item.label != null && String(item.label).trim() !== "") return String(item.label);
    if (item.id) return String(item.id);
    return "";
  }

  function appendPrompt(card, item) {
    if (item.prompt) card.appendChild(el("p", "q-prompt", item.prompt));
    else if (item.stem) card.appendChild(el("p", "q-prompt", item.stem));
  }

  function appendWordBank(card, item) {
    var bank = item.wordBank;
    if (!bank || !bank.length) return;
    var wrap = el("div", "q-word-bank");
    wrap.appendChild(el("div", "q-word-bank__label", "Word bank"));
    var chips = el("div", "q-word-bank__chips");
    bank.forEach(function (word) {
      var btn = el("button", "q-word-chip", String(word));
      btn.type = "button";
      btn.addEventListener("click", function () {
        var input = card.querySelector(".q-text-input");
        if (!input) return;
        var sep = input.value && !/\s$/.test(input.value) ? " " : "";
        input.value = input.value + sep + word;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.focus();
      });
      chips.appendChild(btn);
    });
    wrap.appendChild(chips);
    card.appendChild(wrap);
  }

  function appendClipAudio(card, item) {
    var clip = item.audioClip || item.clip;
    if (!clip) return;
    var s = String(clip).trim();
    var url;
    if (/^https?:\/\//i.test(s)) url = s;
    else if (s.indexOf("audio/") === 0) url = root.stepupUrl(s);
    else url = root.stepupUrl("audio/" + s);
    var wrap = el("div", "q-clip-audio");
    var media = document.createElement("audio");
    media.controls = true;
    media.preload = "metadata";
    media.className = "stepup-audio stepup-audio--clip";
    media.src = url;
    wrap.appendChild(media);
    card.appendChild(wrap);
  }

  function appendItemPagePhoto(card, item, skipPhotoField) {
    return;
  }

  function itemType(item) {
    return String((item && item.type) || "choice").trim();
  }

  function isSelfcheckType(type) {
    return type === "selfcheck" || type === "repeat" || type === "listen-repeat";
  }

  function renderDisplayOnlyItem(item, practice, passageShown) {
    var card = el("article", "q-card q-card--display");
    if (item.label) card.appendChild(el("div", "q-label", String(item.label)));
    appendPassageBlock(card, item, practice, passageShown);
    appendItemPagePhoto(card, item, false);
    if (item.photo) {
      appendPhotoBlock(card, item.photo, "Illustration");
    }
    appendPrompt(card, item);
    if (item.target || item.phrase) {
      card.appendChild(el("p", "q-display-target", item.target || item.phrase));
    }
    appendClipAudio(card, item);
    return card;
  }

  function renderChoiceItem(item, responses, practice, passageShown) {
    var card = el("article", "q-card");
    card.appendChild(el("div", "q-label", formatItemLabel(item)));
    appendPassageBlock(card, item, practice, passageShown);
    appendItemPagePhoto(card, item, true);
    if (item.photo) {
      appendPhotoBlock(card, item.photo, "Picture for question " + (item.label || item.id));
    }
    appendPrompt(card, item);
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

  function renderTextItem(item, responses, practice, passageShown) {
    var card = el("article", "q-card q-card--text");
    card.appendChild(el("div", "q-label", formatItemLabel(item)));
    appendPassageBlock(card, item, practice, passageShown);
    appendItemPagePhoto(card, item, true);
    if (item.photo) {
      appendPhotoBlock(card, item.photo, "Picture for question " + formatItemLabel(item));
    }
    appendPrompt(card, item);
    appendWordBank(card, item);
    var input = document.createElement("input");
    input.type = "text";
    input.className = "q-text-input";
    input.name = item.id;
    input.setAttribute("autocomplete", "off");
    input.setAttribute("spellcheck", "true");
    input.setAttribute("aria-label", "Your answer for question " + (item.label || item.id));
    input.dataset.textId = item.id;
    var current = responses[item.id] && responses[item.id].value;
    if (current) input.value = current;
    input.addEventListener("input", function () {
      responses[item.id] = { value: input.value };
    });
    card.appendChild(input);
    card.dataset.itemId = item.id;
    return card;
  }

  function renderTfItem(item, responses, practice, passageShown) {
    var tfItem = Object.assign({}, item, {
      type: "choice",
      choices: item.choices || { A: "True", B: "False" },
    });
    var card = renderChoiceItem(tfItem, responses, practice, passageShown);
    card.classList.add("q-card--tf");
    return card;
  }

  function renderSelfcheckItem(item, responses, practice, passageShown) {
    var card = el("article", "q-card q-card--selfcheck");
    card.appendChild(el("div", "q-label", item.label ? String(item.label) : "Listen & repeat"));
    appendPassageBlock(card, item, practice, passageShown);
    appendItemPagePhoto(card, item, true);
    if (item.photo) {
      appendPhotoBlock(card, item.photo, "Picture for this activity");
    }
    appendPrompt(card, item);
    var phrase = item.target || item.phrase;
    if (phrase) {
      card.appendChild(el("p", "q-selfcheck-target", phrase));
    }
    appendClipAudio(card, item);
    var showType = item.inputMode || item.mode || "both";
    var resp = responses[item.id] || {};
    if (showType === "both" || showType === "type" || showType === "text") {
      appendWordBank(card, item);
      var input = document.createElement("input");
      input.type = "text";
      input.className = "q-text-input";
      input.name = item.id + "_typed";
      input.setAttribute("autocomplete", "off");
      input.setAttribute("spellcheck", "true");
      input.setAttribute("aria-label", "Type what you heard");
      input.dataset.textId = item.id;
      if (resp.value) input.value = resp.value;
      input.addEventListener("input", function () {
        responses[item.id] = Object.assign({}, responses[item.id] || {}, { value: input.value });
      });
      card.appendChild(input);
    }
    if (showType === "both" || showType === "heard" || item.allowHeard !== false) {
      var heardRow = el("label", "q-heard-row");
      var heard = document.createElement("input");
      heard.type = "checkbox";
      heard.dataset.heardId = item.id;
      if (resp.heard) heard.checked = true;
      heard.addEventListener("change", function () {
        responses[item.id] = Object.assign({}, responses[item.id] || {}, { heard: heard.checked });
      });
      heardRow.appendChild(heard);
      heardRow.appendChild(document.createTextNode(" I repeated this aloud (self-check)"));
      card.appendChild(heardRow);
    }
    card.dataset.itemId = item.id;
    return card;
  }

  function renderMatchItem(item, responses, practice, passageShown) {
    var card = el("article", "q-card q-card--match");
    card.appendChild(el("div", "q-label", formatItemLabel(item)));
    appendPassageBlock(card, item, practice, passageShown);
    var pageRef = itemPageImageRef(item);
    if (pageRef) {
      appendPhotoBlock(card, pageRef, "Picture page for matching");
    } else if (item.photo) {
      appendPhotoBlock(card, item.photo, "Picture page for matching");
    }
    appendPrompt(card, item);
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
      if (root.STEPUP_QUIZ && root.STEPUP_QUIZ.isScoredItem) {
        if (!root.STEPUP_QUIZ.isScoredItem(item)) return;
      } else if (item.displayOnly) return;
      var type = itemType(item);
      if (type === "match") {
        var links = {};
        var card = form.querySelector('[data-match-id="' + item.id + '"]');
        if (card) {
          card.querySelectorAll("select").forEach(function (sel, idx) {
            var left = item.pairs[idx].left;
            links[left] = sel.value;
          });
        }
        responses[item.id] = { links: links };
      } else if (type === "text" || type === "typed" || type === "fill") {
        var textEl = form.querySelector('[data-text-id="' + item.id + '"]');
        responses[item.id] = { value: textEl ? textEl.value : "" };
      } else if (isSelfcheckType(type)) {
        var typed = form.querySelector('[data-text-id="' + item.id + '"]');
        var heardEl = form.querySelector('[data-heard-id="' + item.id + '"]');
        responses[item.id] = {
          value: typed ? typed.value : "",
          heard: !!(heardEl && heardEl.checked),
        };
      } else {
        var picked = form.querySelector('input[name="' + item.id + '"]:checked');
        responses[item.id] = { value: picked ? picked.value : "" };
      }
    });
    return responses;
  }

  function renderQuizItem(item, responses, practice, passageShown) {
    if (item.displayOnly) return renderDisplayOnlyItem(item, practice, passageShown);
    var type = itemType(item);
    if (type === "match") return renderMatchItem(item, responses, practice, passageShown);
    if (type === "text" || type === "typed" || type === "fill") {
      return renderTextItem(item, responses, practice, passageShown);
    }
    if (type === "tf") return renderTfItem(item, responses, practice, passageShown);
    if (isSelfcheckType(type)) return renderSelfcheckItem(item, responses, practice, passageShown);
    return renderChoiceItem(item, responses, practice, passageShown);
  }

  function renderPractice(app, practiceId) {
    loadCatalog().then(function (c) {
      var meta = c.practiceIndex && c.practiceIndex[practiceId];
      if (!meta) {
        app.innerHTML = "<p>Practice not found.</p>";
        return;
      }
      var trackId = meta.level + "-" + meta.skill;
      var track = (c.tracks || []).find(function (t) {
        return t.trackId === trackId;
      });
      if (track && !practiceUnlocked(track.practices, practiceId)) {
        app.innerHTML = "";
        app.appendChild(renderTopbar(meta.title || practiceId, "#/track/" + trackId));
        var locked = el("div", "locked-panel");
        locked.innerHTML =
          "<p><strong>This practice is locked.</strong></p><p>Score at least " +
          retryPct() +
          "% on the previous exercise to unlock it.</p>";
        var back = el("a", "btn-primary", "Back to map");
        back.href = "#/track/" + trackId;
        locked.appendChild(back);
        app.appendChild(locked);
        return;
      }
      if (root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.touch) {
        root.STEPUP_PROGRESS.touch(practiceId, trackId);
      }
      fetch(root.stepupUrl(meta.dataPath), { cache: "no-cache" })
        .then(function (r) {
          return r.json();
        })
        .then(function (practice) {
          clearPracticeTimer();
          startedAt = Date.now();
          var skill = practice.skill || meta.skill || "rc";
          var items = (practice.items || []).filter(isPlayableItem);
          app.innerHTML = "";
          var title = practice.title || meta.title;
          var sub = practice.subtitle || meta.subtitle;
          app.appendChild(renderTopbar(title, "#/track/" + trackId));

          var timerBar = null;
          var timerClock = null;
          var timerRemaining = 0;
          if (items.length) {
            timerRemaining = secondsPerPlayableItem(skill) * items.length;
            timerBar = el(
              "div",
              "practice-timer",
              'Time left: <span class="practice-timer__clock">' + formatTimer(timerRemaining) + "</span>"
            );
            timerClock = timerBar.querySelector(".practice-timer__clock");
            app.appendChild(timerBar);
          }

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
          var blockedHidden = (practice.items || []).length - items.length;
          if (blockedHidden > 0 && !isContentDebug()) {
            app.appendChild(
              el(
                "p",
                "practice-note",
                blockedHidden +
                  " question(s) from this section are being rewritten and are hidden until the next content update."
              )
            );
          }
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
            var passageShown = {};
            var lastSection = null;
            items.forEach(function (item) {
              if (item.section && item.section !== lastSection) {
                form.appendChild(el("div", "practice-section-banner", item.section));
                lastSection = item.section;
              }
              form.appendChild(renderQuizItem(item, responses, practice, passageShown));
            });
          }

          var actions = el("div", "practice-actions");
          var checkBtn = el("button", "btn-primary", "Check answers");
          checkBtn.type = "button";
          var resultBox = el("div", "result-box", "");
          var graded = false;

          function lockPracticeForm() {
            form.querySelectorAll("input, select, textarea, button").forEach(function (node) {
              node.disabled = true;
            });
          }

          function submitAnswers() {
            if (graded) return;
            graded = true;
            clearPracticeTimer();
            var resp = collectResponses(form, practice);
            var result = root.STEPUP_QUIZ.gradePractice(practice, resp);
            var duration = Math.round((Date.now() - startedAt) / 1000);
            root.STEPUP_SCORES.persist(practice, result, duration);
            var completeNow = practiceComplete(practice.practiceId);
            var needRetry = result.scorePct < retryPct() && !completeNow;
            var resultHtml =
              "<strong>Score: " +
              result.scoreValue +
              " / " +
              result.scoreMax +
              " (" +
              result.scorePct +
              "%)</strong>";
            if (needRetry) {
              resultHtml +=
                '<p class="result-retry-msg">Please try this exercise again (under ' +
                retryPct() +
                "%).</p>";
            } else if (result.scorePct < retryPct() && completeNow) {
              resultHtml +=
                '<p class="result-retry-msg result-retry-msg--soft">Latest attempt under ' +
                retryPct() +
                "%; your best score still counts toward progress.</p>";
            }
            resultBox.innerHTML = resultHtml;
            resultBox.className =
              "result-box result-box--show" + (needRetry ? " result-box--retry" : "");
            var byId = {};
            result.detail.forEach(function (d) {
              byId[d.id] = d;
            });
            form.querySelectorAll(".q-card").forEach(function (card) {
              var id = card.dataset.itemId;
              var detail = byId[id];
              if (!detail) return;
              card.classList.toggle("q-card--correct", detail.correct);
              card.classList.toggle("q-card--wrong", !detail.correct);
            });
            lockPracticeForm();
            checkBtn.disabled = true;
            actions.innerHTML = "";
            if (needRetry) {
              var tryAgain = el("button", "btn-primary", "Try again");
              tryAgain.type = "button";
              tryAgain.addEventListener("click", function () {
                renderPractice(app, practiceId);
              });
              actions.appendChild(tryAgain);
            } else if (track) {
              var idx = -1;
              for (var pi = 0; pi < track.practices.length; pi++) {
                if (track.practices[pi].id === practiceId) {
                  idx = pi;
                  break;
                }
              }
              if (idx >= 0 && idx < track.practices.length - 1) {
                var nextP = track.practices[idx + 1];
                var nextBtn = el("a", "btn-primary", "Next exercise →");
                nextBtn.href = "#/practice/" + nextP.id;
                actions.appendChild(nextBtn);
              }
              var mapBtn = el("a", "btn-secondary", "Back to map");
              mapBtn.href = "#/track/" + trackId;
              actions.appendChild(mapBtn);
            }
          }

          checkBtn.addEventListener("click", submitAnswers);
          actions.appendChild(checkBtn);
          form.appendChild(actions);
          form.appendChild(resultBox);
          app.appendChild(form);

          if (timerBar && timerClock && timerRemaining > 0) {
            practiceTimerId = setInterval(function () {
              timerRemaining -= 1;
              timerClock.textContent = formatTimer(timerRemaining);
              if (timerRemaining <= 60) timerBar.classList.add("practice-timer--warn");
              if (timerRemaining <= 0) submitAnswers();
            }, 1000);
          }
        })
        .catch(function () {
          app.innerHTML = "<p>Could not load practice data.</p>";
        });
    });
  }

  function render() {
    clearPracticeTimer();
    var app = document.getElementById("stepup-app");
    if (!app) return;
    var route = parseRoute();
    if (route.view === "home") renderHome(app);
    else if (route.view === "book") renderBook(app, route.level);
    else if (route.view === "track") renderTrack(app, route.trackId);
    else if (route.view === "practice") renderPractice(app, route.practiceId);
    else renderHome(app);
  }

  function bindProgressRefresh() {
    if (progressUnsub) progressUnsub();
    if (root.STEPUP_PROGRESS && root.STEPUP_PROGRESS.onChange) {
      progressUnsub = root.STEPUP_PROGRESS.onChange(function () {
        var route = parseRoute();
        if (route.view === "practice") return;
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
