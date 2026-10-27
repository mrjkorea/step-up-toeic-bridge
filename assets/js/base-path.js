/* GitHub Pages project site base path */
(function (root) {
  "use strict";
  var path = root.location && root.location.pathname ? root.location.pathname : "/";
  var base = "/";
  if (path.indexOf("/step-up-toeic-bridge") === 0) {
    base = "/step-up-toeic-bridge/";
  } else if (path !== "/" && path.lastIndexOf("/") > 0) {
    base = path.slice(0, path.lastIndexOf("/") + 1);
  }
  root.STEPUP_BASE = base;
  root.stepupUrl = function (rel) {
    rel = String(rel || "").replace(/^\//, "");
    return base + rel;
  };
})(typeof window !== "undefined" ? window : globalThis);
