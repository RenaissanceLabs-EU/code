// Recipe builder: renders an ordered plan from the form and the rules in #rdata (data/recipes.json + the verified catalog).
// The rules are hand-written; this file only matches conditions and renders. No network, no dependencies.
(function () {
  var D = JSON.parse(document.getElementById('rdata').textContent);
  var R = D.resources, REC = D.recipes, SN = D.snippets, ST = D.stages;
  var form = document.getElementById('form'), out = document.getElementById('out');
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function rich(s) { return esc(s).replace(/`([^`]+)`/g, '<code>$1</code>'); }
  function state() {
    var s = { goal: '', start: '', size: '', budget: '', languages: [], data: [] };
    ['goal', 'start', 'size', 'budget'].forEach(function (k) { var el = form.querySelector('input[name=' + k + ']:checked'); s[k] = el ? el.value : ''; });
    ['languages', 'data'].forEach(function (k) { form.querySelectorAll('input[name=' + k + ']:checked').forEach(function (el) { s[k].push(el.value); }); });
    return s;
  }
  function inter(a, list) { return list.some(function (x) { return a.indexOf(x) >= 0; }); }
  function matches(when, s) {
    if (!when) return true;
    for (var k in when) {
      var v = when[k], neg = k.indexOf('not_') === 0, key = neg ? k.slice(4) : k;
      var cur = s[key]; var arr = Array.isArray(cur) ? cur : [cur];
      var hit = inter(arr, v);
      if (neg ? hit : !hit) return false;
    }
    return true;
  }
  function codebox(code, label) {
    return '<div class="codebox"><div class="lab"><span>' + esc(label) + '</span><button class="copy" type="button">Copy</button></div><pre>' + esc(code) + '</pre></div>';
  }
  function label(group, id) { var o = (REC.inputs[group].options || []).filter(function (x) { return x.id === id; })[0]; return o ? o.label : id; }
  function render() {
    var s = state(), html = '';
    var langs = s.languages.length ? s.languages.map(function (l) { return label('languages', l); }).join(', ') : 'no language chosen';
    html += '<div class="summary"><b>Your plan</b><br>Goal: ' + esc(label('goal', s.goal)) + '. Start: ' + esc(label('start', s.start)) + '. Size: ' + esc(label('size', s.size)) + '. Budget: ' + esc(label('budget', s.budget)) + '. Languages: ' + esc(langs) + '.</div>';
    (REC.checks || []).forEach(function (c) { if (matches(c.when, s)) html += '<div class="callout ' + (c.level === 'warn' ? 'warn' : '') + '"><b>' + esc(c.level === 'warn' ? 'Reality check' : 'Note') + '</b>' + rich(c.text) + '</div>'; });
    var n = 0;
    REC.steps.forEach(function (st) {
      if (!matches(st.when, s)) return;
      n++;
      var h = '<section class="stp st-' + esc(st.stage) + '"><header><span class="num">STEP ' + n + '</span><h3>' + esc(st.title) + '</h3></header><div class="body">';
      (st.body || []).forEach(function (b) {
        var t = typeof b === 'string' ? b : b.t, w = typeof b === 'string' ? null : b.when;
        if (matches(w, s)) h += (t.charAt(0) === '-' ? '<ul><li>' + rich(t.slice(1).trim()) + '</li></ul>' : '<p>' + rich(t) + '</p>');
      });
      var picks = (st.picks || []).filter(function (p) { return matches(p.when, s) && R[p.id]; });
      if (picks.length) {
        h += '<div class="picks">';
        picks.forEach(function (p) {
          var r = R[p.id];
          h += '<div class="pick"><a href="/r/' + esc(p.id) + '/">' + esc(r.name) + '</a><span class="why">' + rich(p.why) + '</span><span class="m">' + esc(r.license || 'license not stated') + (r.size ? ' &middot; ' + esc(r.size) : '') + (r.lic_class && r.lic_class !== 'permissive' ? ' &middot; check terms' : '') + '</span></div>';
        });
        h += '</div>';
      }
      (st.snips || []).forEach(function (sid) {
        var sn = SN[sid]; if (!sn) return;
        h += codebox(sn.code, sn.title) + '<p class="snote"><b>Verified:</b> ' + esc(sn.verified_how || '') + '. ' + esc(sn.notes || '') + '</p>';
      });
      (st.pitfalls || []).forEach(function (p) { if (matches(p.when, s)) h += '<div class="pit"><b>Pitfall</b> ' + rich(p.t) + '</div>'; });
      h += '</div></section>';
      html += h;
    });
    html += '<div class="printbar"><button class="btn" type="button" id="print">Print or save as PDF</button><button class="btn" type="button" id="share">Copy link to this plan</button></div>';
    out.innerHTML = html;
    if (window.bindCopy) window.bindCopy(out);
    document.getElementById('print').onclick = function () { window.print(); };
    document.getElementById('share').onclick = function (ev) { var b = ev.target; (navigator.clipboard ? navigator.clipboard.writeText(location.href) : Promise.reject()).then(function () { b.textContent = 'Copied'; }, function () { b.textContent = 'Copy from address bar'; }); };
    // keep the plan in the URL so it can be shared
    var q = []; ['goal', 'start', 'size', 'budget'].forEach(function (k) { q.push(k + '=' + s[k]); }); q.push('languages=' + s.languages.join(',')); q.push('data=' + s.data.join(','));
    try { history.replaceState(null, '', '#' + q.join('&')); } catch (e) {}
  }
  function fromHash() {
    var h = location.hash.replace(/^#/, ''); if (!h) return;
    h.split('&').forEach(function (kv) {
      var p = kv.split('='), k = p[0], v = decodeURIComponent(p[1] || '');
      var els = form.querySelectorAll('input[name=' + k + ']'); if (!els.length) return;
      var vals = v ? v.split(',') : [];
      els.forEach(function (el) { el.checked = vals.indexOf(el.value) >= 0; });
    });
  }
  form.addEventListener('change', render);
  fromHash(); render();
})();
