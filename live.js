// Check allsky-map for a newer frame every 5 minutes (the camera's own upload cadence
// is separate); show an offline note if the image fails to load.
(function () {
  var img = document.getElementById('live-sky');
  var meta = document.getElementById('live-meta');
  if (!img) return;
  var box = img.closest('.live');
  var base = img.getAttribute('src');
  var EVERY = 5 * 60 * 1000;

  function stamp() {
    var t = new Date();
    meta.textContent = 'Last checked for a new frame at ' +
      t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' your time.';
  }

  img.addEventListener('load', function () { box.classList.remove('offline'); stamp(); });
  img.addEventListener('error', function () {
    box.classList.add('offline');
    meta.textContent = 'The camera is offline at the moment.';
  });
  if (img.complete && img.naturalWidth) stamp();

  setInterval(function () {
    if (document.visibilityState === 'visible') img.src = base + '?t=' + Date.now();
  }, EVERY);
})();
