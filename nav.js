// Highlight the sidebar link for the section or paper currently on screen.
(function () {
  var links = {};
  document.querySelectorAll('.side a[href^="#"]').forEach(function (a) {
    var id = a.getAttribute('href').slice(1);
    if (id !== 'top') links[id] = a;
  });

  // page order, so the last one scrolled past is the most specific
  var targets = Object.keys(links)
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean)
    .sort(function (a, b) {
      return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
    });
  if (!targets.length) return;

  function update() {
    // a little below where an anchor jump lands (scroll-margin-top: 2rem)
    var line = 120;
    var current = null;
    targets.forEach(function (t) {
      if (t.getBoundingClientRect().top <= line) current = t.id;
    });
    // the page can't scroll the last papers up to the line, so at the bottom
    // take the last one that is on screen
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
      targets.forEach(function (t) {
        if (t.getBoundingClientRect().top < window.innerHeight * 0.6) current = t.id;
      });
    }
    // after a menu jump, keep the clicked item until the reader scrolls
    if (pinned) current = pinned;
    Object.keys(links).forEach(function (id) {
      links[id].classList.toggle('active', id === current);
    });
  }

  var pinned = null;
  function pinFromHash() {
    var id = location.hash.slice(1);
    pinned = links[id] ? id : null;
    update();
  }
  ['wheel', 'touchmove', 'keydown'].forEach(function (ev) {
    window.addEventListener(ev, function () {
      if (pinned) { pinned = null; update(); }
    }, { passive: true });
  });
  window.addEventListener('hashchange', pinFromHash);
  document.querySelectorAll('.side a[href^="#"]').forEach(function (a) {
    // a second click on the same link fires no hashchange
    a.addEventListener('click', function () { setTimeout(pinFromHash, 0); });
  });

  var queued = false;
  window.addEventListener('scroll', function () {
    if (queued) return;
    queued = true;
    requestAnimationFrame(function () { queued = false; update(); });
  }, { passive: true });
  window.addEventListener('resize', update);
  window.addEventListener('load', update);
  pinFromHash();
})();
