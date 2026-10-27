/* In-quiz LC audio from audio/manifest.json */
(function (root) {
  "use strict";

  var manifest = null;
  var loadPromise = null;

  function loadManifest() {
    if (manifest) return Promise.resolve(manifest);
    if (loadPromise) return loadPromise;
    var url = root.stepupUrl("audio/manifest.json?v=1");
    loadPromise = fetch(url, { cache: "no-cache" })
      .then(function (r) {
        if (!r.ok) throw new Error("manifest");
        return r.json();
      })
      .then(function (m) {
        manifest = m;
        return m;
      })
      .catch(function () {
        loadPromise = null;
        return null;
      });
    return loadPromise;
  }

  function entryForRef(audioRef) {
    if (!manifest || !audioRef) return null;
    var practices = manifest.practices || {};
    return practices[audioRef] || null;
  }

  function mount(container, audioRef) {
    if (!container) return;
    container.innerHTML = "";
    return loadManifest().then(function () {
      var entry = entryForRef(audioRef);
      if (!entry || !entry.files || !entry.files.length) {
        container.innerHTML = '<p class="audio-missing">Audio will be added for this practice.</p>';
        return;
      }
      entry.files.forEach(function (file, idx) {
        var wrap = document.createElement("div");
        wrap.className = "audio-block";
        if (entry.files.length > 1) {
          var lab = document.createElement("div");
          lab.className = "audio-label";
          lab.textContent = "Track " + String.fromCharCode(65 + idx);
          wrap.appendChild(lab);
        }
        var video = document.createElement("video");
        video.controls = true;
        video.preload = "metadata";
        video.className = "stepup-audio";
        video.src = root.stepupUrl("audio/" + file);
        wrap.appendChild(video);
        container.appendChild(wrap);
      });
    });
  }

  root.STEPUP_AUDIO = { mount: mount, loadManifest: loadManifest };
})(typeof window !== "undefined" ? window : globalThis);
