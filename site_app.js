// Renaissance Labs Code: theme toggle, copy buttons, catalog filters, loss-signal figure. No dependencies.
(function () {
  var root = document.documentElement;
  var tbtn = document.getElementById('theme');
  if (tbtn) tbtn.addEventListener('click', function () {
    var dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('theme', root.dataset.theme); } catch (e) {}
  });
  window.bindCopy = function (scope) {
    (scope || document).querySelectorAll('.copy').forEach(function (b) {
      if (b.dataset.bound) return; b.dataset.bound = '1';
      b.addEventListener('click', function () {
        var text = b.closest('.codebox').querySelector('pre').innerText;
        (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(function () {
          b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1400);
        }, function () { b.textContent = 'Select and copy'; });
      });
    });
  };
  bindCopy();

  // ---- catalog filters (state lives in the URL hash so a filtered view can be shared)
  var grid = document.getElementById('grid');
  if (grid) {
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.rc'));
    var state = { q: '', stage: '', kind: '', lang: '', task: '', lic: '', layer: '', level: '' };
    var qi = document.getElementById('q'), cnt = document.getElementById('cnt'), none = document.getElementById('none');
    var sels = { kind: document.getElementById('f-kind'), lang: document.getElementById('f-lang'), task: document.getElementById('f-task'), lic: document.getElementById('f-lic'), layer: document.getElementById('f-layer'), level: document.getElementById('f-level') };
    var stageBtns = Array.prototype.slice.call(document.querySelectorAll('.chipb[data-stage]'));
    function readHash() {
      var h = location.hash.replace(/^#/, '');
      Object.keys(state).forEach(function (k) { state[k] = ''; });
      h.split('&').forEach(function (kv) { var p = kv.split('='); if (p[0] in state && p[1] !== undefined) state[p[0]] = decodeURIComponent(p[1]); });
    }
    function writeHash() {
      var parts = Object.keys(state).filter(function (k) { return state[k]; }).map(function (k) { return k + '=' + encodeURIComponent(state[k]); });
      history.replaceState(null, '', parts.length ? '#' + parts.join('&') : location.pathname + location.search);
    }
    function has(attr, v) { return (' ' + attr + ' ').indexOf(' ' + v + ' ') >= 0; }
    function apply() {
      var terms = state.q.toLowerCase().split(/\s+/).filter(Boolean), n = 0;
      cards.forEach(function (c) {
        var d = c.dataset;
        var ok = (!state.stage || has(d.stage, state.stage)) && (!state.kind || d.kind === state.kind) && (!state.lang || has(d.lang, state.lang)) &&
          (!state.task || has(d.task, state.task)) && (!state.lic || d.lic === state.lic) && (!state.layer || has(d.layer, state.layer)) && (!state.level || has(d.level, state.level)) && terms.every(function (t) { return d.s.indexOf(t) >= 0; });
        c.hidden = !ok; if (ok) n++;
      });
      cnt.textContent = n + (n === 1 ? ' resource' : ' resources');
      none.hidden = n > 0;
      qi.value = state.q;
      Object.keys(sels).forEach(function (k) { sels[k].value = state[k]; });
      stageBtns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.stage === state.stage)); });
    }
    qi.addEventListener('input', function () { state.q = qi.value; writeHash(); apply(); });
    Object.keys(sels).forEach(function (k) { sels[k].addEventListener('change', function () { state[k] = sels[k].value; writeHash(); apply(); }); });
    stageBtns.forEach(function (b) { b.addEventListener('click', function () { state.stage = state.stage === b.dataset.stage ? '' : b.dataset.stage; writeHash(); apply(); }); });
    var reset = document.getElementById('reset');
    if (reset) reset.addEventListener('click', function () { Object.keys(state).forEach(function (k) { state[k] = ''; }); writeHash(); apply(); });
    window.addEventListener('hashchange', function () { readHash(); apply(); });
    readHash(); apply();
  }

  // ---- dataset directory: show one kind of resource
  var dsb = Array.prototype.slice.call(document.querySelectorAll('.chipb[data-k]'));
  if (dsb.length) {
    var dsk = '';
    function dsapply() {
      document.querySelectorAll('table.ds tbody tr').forEach(function (r) { r.hidden = !!dsk && r.dataset.kind !== dsk; });
      document.querySelectorAll('.dsec').forEach(function (s) { s.hidden = !s.querySelector('tbody tr:not([hidden])'); });
      dsb.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.k === dsk)); });
    }
    dsb.forEach(function (b) { b.addEventListener('click', function () { dsk = dsk === b.dataset.k ? '' : b.dataset.k; dsapply(); }); });
    document.getElementById('dsreset').addEventListener('click', function () { dsk = ''; dsapply(); });
  }

  // ---- reading list filters
  var rg = document.getElementById('rgrid');
  if (rg) {
    var rcards = Array.prototype.slice.call(rg.querySelectorAll('.rd')), rs = { q: '', stage: '', type: '', level: '' };
    var rq = document.getElementById('rq'), rt = document.getElementById('rf-type'), rl = document.getElementById('rf-level'), rc = document.getElementById('rcnt'), rn = document.getElementById('rnone');
    var rchips = Array.prototype.slice.call(document.querySelectorAll('.chipb[data-stage]'));
    function rhas(attr, v) { return (' ' + attr + ' ').indexOf(' ' + v + ' ') >= 0; }
    function rapply() {
      var terms = rs.q.toLowerCase().split(/\s+/).filter(Boolean), n = 0;
      rcards.forEach(function (c) { var d = c.dataset, ok = (!rs.stage || rhas(d.stage, rs.stage)) && (!rs.type || d.type === rs.type) && (!rs.level || d.level === rs.level) && terms.every(function (t) { return d.s.indexOf(t) >= 0; }); c.hidden = !ok; if (ok) n++; });
      rc.textContent = n + (n === 1 ? ' item' : ' items'); rn.hidden = n > 0;
      rchips.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.stage === rs.stage)); });
    }
    rq.addEventListener('input', function () { rs.q = rq.value; rapply(); });
    rt.addEventListener('change', function () { rs.type = rt.value; rapply(); });
    rl.addEventListener('change', function () { rs.level = rl.value; rapply(); });
    rchips.forEach(function (b) { b.addEventListener('click', function () { rs.stage = rs.stage === b.dataset.stage ? '' : b.dataset.stage; rapply(); }); });
    document.getElementById('rreset').addEventListener('click', function () { rs = { q: '', stage: '', type: '', level: '' }; rq.value = ''; rt.value = ''; rl.value = ''; rapply(); });
    rapply();
  }

  // ---- figure: why verifiable-reward RL needs a middle band of difficulty
  var fig = document.getElementById('gradfig');
  if (fig) {
    var G = 8;
    var range = document.getElementById('gradp'), out = document.getElementById('gradv'), bars = fig.querySelector('#gradbars'), txt = document.getElementById('gradtxt');
    function draw() {
      var p = parseFloat(range.value), html = '', i;
      var pAllSame = Math.pow(p, G) + Math.pow(1 - p, G);   // chance that all G rollouts get the same reward
      var useful = 1 - pAllSame;
      for (i = 0; i <= 10; i++) {
        var q = i / 10, same = Math.pow(q, G) + Math.pow(1 - q, G), u = 1 - same;
        var x = 40 + i * 52, h = u * 150, cur = Math.abs(q - p) < 0.05;
        html += '<rect x="' + (x - 18) + '" y="' + (190 - h) + '" width="36" height="' + h + '" rx="4" fill="' + (cur ? 'var(--accent)' : 'var(--rule-strong)') + '"/>';
        html += '<text x="' + x + '" y="210" text-anchor="middle" font-size="11" fill="var(--ink-faint)" font-family="var(--mono)">' + Math.round(q * 100) + '%</text>';
      }
      bars.innerHTML = html;
      out.textContent = Math.round(p * 100) + '%';
      txt.textContent = 'With ' + G + ' rollouts per task, a task the model solves ' + Math.round(p * 100) + '% of the time gives a non-zero learning signal in ' + Math.round(useful * 100) + '% of groups.';
    }
    range.addEventListener('input', draw); draw();
  }
})();
