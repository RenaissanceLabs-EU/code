// Live figures. Each <figure data-fig="name"> is filled in here. The program figures run on Mini (lang.js), a real
// lexer, parser, type checker, compiler and stack machine, so what you see is computed from what you type.
(function () {
  'use strict';
  var M = window.Mini;
  var GCD = "# Euclid's algorithm, about 300 BC\nfn gcd(a, b) {\n  while b != 0 {\n    t = a % b\n    a = b\n    b = t\n  }\n  return a\n}\nprint(gcd(48, 18))\n";
  var GCD_FN = "fn gcd(a, b) {\n  while b != 0 {\n    t = a % b\n    a = b\n    b = t\n  }\n  return a\n}\n";
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function el(tag, cls, html) { var x = document.createElement(tag); if (cls) x.className = cls; if (html !== undefined) x.innerHTML = html; return x; }
  function editor(parent, src, rows) {
    var t = el('textarea', 'lab-ed'); t.value = src; t.rows = rows || src.split('\n').length; t.spellcheck = false;
    t.setAttribute('autocapitalize', 'off'); t.setAttribute('autocomplete', 'off'); t.setAttribute('autocorrect', 'off'); t.setAttribute('aria-label', 'Program source, editable');
    t.addEventListener('keydown', function (ev) { if (ev.key === 'Tab') { ev.preventDefault(); var s = t.selectionStart; t.value = t.value.slice(0, s) + '  ' + t.value.slice(t.selectionEnd); t.selectionStart = t.selectionEnd = s + 2; t.dispatchEvent(new Event('input')); } });
    parent.appendChild(t); return t;
  }
  function btn(parent, label, fn, cls) { var b = el('button', 'lab-btn' + (cls ? ' ' + cls : ''), esc(label)); b.type = 'button'; b.addEventListener('click', fn); parent.appendChild(b); return b; }
  function where(src, pos) { var before = src.slice(0, pos), line = before.split('\n').length, col = pos - before.lastIndexOf('\n'); return 'line ' + line + ', column ' + col; }
  function errHtml(src, er) {
    if (!er || er.msg === undefined) return '<div class="lab-err">' + esc(String(er)) + '</div>';
    var ls = src.lastIndexOf('\n', er.s - 1) + 1, le = src.indexOf('\n', er.s); if (le < 0) le = src.length;
    var line = src.slice(ls, le), a = er.s - ls, b = Math.max(a + 1, Math.min(er.e, le) - ls);
    return '<div class="lab-err"><b>' + esc(er.msg) + '</b><span>' + esc(where(src, er.s)) + '</span><pre>' + esc(line.slice(0, a)) + '<mark>' + esc(line.slice(a, b) || ' ') + '</mark>' + esc(line.slice(b)) + '</pre></div>';
  }
  function safe(fn, src, out) { try { return fn(); } catch (er) { out.innerHTML = errHtml(src, er); return null; } }
  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  var redraws = [];
  var tb = document.getElementById('theme'); if (tb) tb.addEventListener('click', function () { setTimeout(function () { redraws.forEach(function (f) { f(); }); }, 30); });
  if (window.matchMedia) { try { matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () { redraws.forEach(function (f) { f(); }); }); } catch (e) {} }

  var F = {};

  // ---------------------------------------------------------------- text: characters -> code points -> bytes
  F.bytes = function (fig) {
    var inp = el('input', 'lab-in'); inp.type = 'text'; inp.value = 'a = b % 2  # é ≠ 🙂'; inp.maxLength = 40; inp.setAttribute('aria-label', 'Text to encode'); inp.spellcheck = false;
    var out = el('div', 'bytes'), sum = el('p', 'lab-sum'); fig.appendChild(inp); fig.appendChild(out); fig.appendChild(sum);
    var enc = new TextEncoder();
    function draw() {
      var chars = Array.from(inp.value), html = '', total = 0;
      chars.forEach(function (ch) {
        var b = enc.encode(ch), cp = ch.codePointAt(0).toString(16).toUpperCase(); total += b.length;
        while (cp.length < 4) cp = '0' + cp;
        html += '<div class="bcell n' + b.length + '"><span class="ch">' + (ch === ' ' ? '␣' : esc(ch)) + '</span><span class="cp">U+' + cp + '</span><span class="bx">' + Array.prototype.map.call(b, function (x) { return (x < 16 ? '0' : '') + x.toString(16).toUpperCase(); }).join(' ') + '</span></div>';
      });
      out.innerHTML = html;
      sum.textContent = chars.length + ' characters become ' + total + ' bytes in UTF-8. The machine stores only the bottom row.';
    }
    inp.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- tokens
  function tokensHtml(src) {
    var toks = M.lex(src), html = '', counts = {};
    toks.forEach(function (t) {
      if (t.t === 'eof') return;
      if (t.t === 'nl' && t.v === '\n') { html += '<br>'; return; }
      var kind = t.t === 'nl' ? 'punct' : t.t; counts[kind] = (counts[kind] || 0) + 1;
      html += '<span class="tk tk-' + kind + '" title="' + kind + '">' + esc(t.v) + '</span>';
    });
    return { html: html, counts: counts, n: toks.filter(function (t) { return t.t !== 'eof' && t.t !== 'nl' && t.t !== 'comment'; }).length };
  }
  var KIND = { kw: 'keywords', id: 'names', num: 'numbers', op: 'operators', punct: 'punctuation', comment: 'comments' };
  F.tokens = function (fig) {
    var ed = editor(fig, GCD), out = el('div', 'toks'), sum = el('p', 'lab-sum'); fig.appendChild(out); fig.appendChild(sum);
    function draw() {
      var r = safe(function () { return tokensHtml(ed.value); }, ed.value, out); if (!r) { sum.textContent = ''; return; }
      out.innerHTML = r.html || '<span class="lab-dim">Nothing to read yet.</span>';
      sum.innerHTML = ed.value.length + ' characters became ' + r.n + ' tokens: ' + Object.keys(KIND).filter(function (k) { return r.counts[k]; }).map(function (k) { return '<span class="tk tk-' + k + '">' + r.counts[k] + ' ' + KIND[k] + '</span>'; }).join(' ') + '. Spaces are gone, and the comment will be dropped before parsing.';
    }
    ed.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- tree
  function kids(n) {
    switch (n.k) {
      case 'Program': return n.fns.concat(n.body);
      case 'Fn': return n.body;
      case 'Assign': return [{ k: 'Name', name: n.name }, n.value];
      case 'If': return [n.cond, { k: 'Block', label: 'then', body: n.then }].concat(n['else'] ? [{ k: 'Block', label: 'else', body: n['else'] }] : []);
      case 'While': return [n.cond, { k: 'Block', label: 'do', body: n.body }];
      case 'Block': return n.body;
      case 'Return': return n.value ? [n.value] : [];
      case 'ExprStmt': return [n.expr];
      case 'Bin': return [n.l, n.r];
      case 'Un': case 'Paren': return [n.e1];
      case 'Call': return n.args;
      default: return [];
    }
  }
  function label(n) {
    switch (n.k) {
      case 'Program': return 'program'; case 'Fn': return 'fn ' + n.name + '(' + n.params.join(', ') + ')';
      case 'Assign': return '='; case 'Name': return n.name; case 'If': return 'if'; case 'While': return 'while'; case 'Block': return n.label;
      case 'Return': return 'return'; case 'ExprStmt': return 'do'; case 'Bin': return n.op; case 'Un': return n.op; case 'Paren': return '( )';
      case 'Call': return n.name + '( )'; case 'Num': return String(n.v); case 'Bool': return String(n.v); case 'Var': return n.name;
    }
  }
  function cls(n) { return n.k === 'Num' || n.k === 'Bool' ? 'lit' : n.k === 'Var' || n.k === 'Name' ? 'nm' : n.k === 'Bin' || n.k === 'Un' || n.k === 'Assign' ? 'op' : 'st'; }
  function treeSvg(root) {
    var x = 0, nodes = [], edges = [], maxd = 0, UNIT = 9;
    function w(n) { return Math.max(34, label(n).length * UNIT + 18); }
    function lay(n, d) {
      var ch = kids(n).map(function (c) { return lay(c, d + 1); }), me = { n: n, d: d, w: w(n) };
      if (!ch.length) { me.x = x + me.w / 2; x += me.w + 14; }
      else { me.x = (ch[0].x + ch[ch.length - 1].x) / 2; var need = me.x - me.w / 2; if (need < 0) { /* never: leaves start at 0 */ } ch.forEach(function (c) { edges.push([me, c]); }); }
      maxd = Math.max(maxd, d); nodes.push(me); return me;
    }
    lay(root, 0);
    var minx = Math.min.apply(null, nodes.map(function (m) { return m.x - m.w / 2; })), maxx = Math.max.apply(null, nodes.map(function (m) { return m.x + m.w / 2; }));
    var W = maxx - minx + 8, H = (maxd + 1) * 58 + 8, s = '';
    function Y(d) { return d * 58 + 22; }
    edges.forEach(function (e2) { s += '<line x1="' + (e2[0].x - minx + 4) + '" y1="' + (Y(e2[0].d) + 14) + '" x2="' + (e2[1].x - minx + 4) + '" y2="' + (Y(e2[1].d) - 14) + '" class="edge"/>'; });
    nodes.forEach(function (m) { s += '<g class="tn tn-' + cls(m.n) + '"><rect x="' + (m.x - minx + 4 - m.w / 2) + '" y="' + (Y(m.d) - 14) + '" width="' + m.w + '" height="28" rx="8"/><text x="' + (m.x - minx + 4) + '" y="' + (Y(m.d) + 5) + '" text-anchor="middle">' + esc(label(m.n)) + '</text></g>'; });
    return { svg: '<svg class="tree" viewBox="0 0 ' + W + ' ' + H + '" style="min-width:' + Math.min(W, 1400) + 'px;max-width:' + W * 1.25 + 'px" role="img" aria-label="Syntax tree">' + s + '</svg>', count: nodes.length, depth: maxd + 1 };
  }
  function outline(n, d) {
    var s = '<div class="ol" style="padding-left:' + (d * 18) + 'px"><span class="tn-' + cls(n) + '">' + esc(label(n)) + '</span></div>';
    kids(n).forEach(function (c) { s += outline(c, d + 1); }); return s;
  }
  function unwrap(prog) { return prog.fns.length === 0 && prog.body.length === 1 ? (prog.body[0].k === 'ExprStmt' ? prog.body[0].expr : prog.body[0]) : prog; }
  F.tree = function (fig) {
    var inp = el('input', 'lab-in'); inp.type = 'text'; inp.value = 't = a % b + 2 * (a - 1)'; inp.spellcheck = false; inp.setAttribute('aria-label', 'One line of code');
    var row = el('div', 'lab-row'), out = el('div', 'treebox'), sum = el('p', 'lab-sum');
    fig.appendChild(inp); fig.appendChild(row); fig.appendChild(out); fig.appendChild(sum);
    ['1 + 2 * 3', '(1 + 2) * 3', 'a < b && !done', 'print(gcd(48, 18))', 'if n % 2 == 0 { n = n / 2 } else { n = 3 * n + 1 }'].forEach(function (p) { btn(row, p, function () { inp.value = p; draw(); }, 'mono'); });
    function draw() {
      var r = safe(function () { return treeSvg(unwrap(M.parse(inp.value))); }, inp.value, out); if (!r) { sum.textContent = ''; return; }
      out.innerHTML = r.svg; sum.textContent = r.count + ' nodes, ' + r.depth + ' levels deep. Lower in the tree means computed earlier.';
    }
    inp.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- types
  function typesHtml(src) {
    var t = M.check(M.parse(src)), html = '<table class="ty">';
    t.fns.forEach(function (f) {
      html += '<tr><th>' + esc(f.name) + '</th><td><span class="mono">(' + f.params.map(function (p) { return esc(p.name) + ': <b>' + p.type + '</b>'; }).join(', ') + ') → <b>' + f.ret + '</b></span>' +
        (f.locals.length ? '<small>inside: ' + f.locals.map(function (p) { return esc(p.name) + ': <b>' + p.type + '</b>'; }).join(', ') + '</small>' : '') + '</td></tr>';
    });
    t.vars.forEach(function (v) { html += '<tr><th>' + esc(v.name) + '</th><td><span class="mono"><b>' + v.type + '</b></span></td></tr>'; });
    return html + '</table>';
  }
  F.types = function (fig) {
    var row = el('div', 'lab-row'), ed = editor(fig, GCD), out = el('div', 'tyout'), sum = el('p', 'lab-sum');
    fig.insertBefore(row, ed); fig.appendChild(out); fig.appendChild(sum);
    var P = [['A working program', GCD], ['Pass true where a number belongs', GCD.replace('gcd(48, 18)', 'gcd(48, true)')], ['Use a number as a condition', GCD.replace('while b != 0', 'while b')],
      ['Return two kinds of value', "fn sign(n) {\n  if n < 0 {\n    return false\n  }\n  return n\n}\nprint(sign(3))\n"], ['Forget a return', "fn half(n) {\n  if n % 2 == 0 {\n    return n / 2\n  }\n}\nx = half(7)\n"]];
    P.forEach(function (p) { btn(row, p[0], function () { ed.value = p[1]; draw(); }); });
    function draw() {
      var r = safe(function () { return typesHtml(ed.value); }, ed.value, out);
      if (r === null) { sum.innerHTML = 'Rejected <b>before running</b>. No test was needed to find this.'; return; }
      out.innerHTML = r || '<span class="lab-dim">No names yet.</span>'; sum.innerHTML = 'Accepted. Nobody wrote a type: every one above was <b>inferred</b> from how the names are used.';
    }
    ed.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- execution: step the machine
  F.exec = function (fig) {
    var ed = editor(fig, GCD), row = el('div', 'lab-row'), grid = el('div', 'exgrid'), sum = el('p', 'lab-sum');
    fig.appendChild(row); fig.appendChild(grid); fig.appendChild(sum);
    var vm = null, built = null, timer = null;
    function stop() { if (timer) { clearInterval(timer); timer = null; runB.textContent = 'Run'; } }
    function reset() { stop(); built = null; vm = null; try { built = M.build(ed.value); vm = new M.VM(built.code); } catch (er) { grid.innerHTML = errHtml(ed.value, er); sum.textContent = ''; return; } draw(); }
    function val(v) { return v === null ? 'nothing' : String(v); }
    function draw() {
      if (!vm) return;
      var f = vm.frame(), ins = vm.current(), src = ed.value, code = built.code[f.fn].code;
      var sh = ins && ins.e > ins.s && !vm.done ? esc(src.slice(0, ins.s)) + '<mark>' + esc(src.slice(ins.s, ins.e)) + '</mark>' + esc(src.slice(ins.e)) : esc(src);
      var list = code.map(function (c, i) { return '<li' + (i === f.pc && !vm.done ? ' class="pc"' : '') + '><i>' + i + '</i>' + esc(M.fmtIns(c)) + '</li>'; }).join('');
      var stack = f.stack.length ? f.stack.map(function (v) { return '<span class="cellv">' + esc(val(v)) + '</span>'; }).join('') : '<span class="lab-dim">empty</span>';
      var locs = Object.keys(f.locals).length ? Object.keys(f.locals).map(function (k) { return '<span class="cellv"><i>' + esc(k) + '</i>' + esc(val(f.locals[k])) + '</span>'; }).join('') : '<span class="lab-dim">none yet</span>';
      var calls = vm.frames.map(function (x) { return esc(x.fn); }).join(' → ');
      grid.innerHTML = '<div class="expane"><h4>Source</h4><pre class="exsrc">' + sh + '</pre></div>' +
        '<div class="expane"><h4>Instructions: ' + esc(f.fn) + '</h4><ol class="exins">' + list + '</ol></div>' +
        '<div class="expane"><h4>Working stack</h4><div class="cells">' + stack + '</div><h4>Variables</h4><div class="cells">' + locs + '</div><h4>Call stack</h4><p class="mono">' + calls + '</p><h4>Output</h4><pre class="exout">' + esc(vm.out.join('\n')) + (vm.error ? '\n' + esc(vm.error.msg) : '') + '</pre></div>';
      var pcEl = grid.querySelector('.pc'); if (pcEl && pcEl.scrollIntoView) { var ol = pcEl.parentNode; ol.scrollTop = Math.max(0, pcEl.offsetTop - ol.offsetTop - ol.clientHeight / 2); }
      sum.textContent = vm.done ? (vm.error ? 'Stopped after ' + vm.steps + ' steps: ' + vm.error.msg : 'Finished in ' + vm.steps + ' steps.') : 'Step ' + vm.steps + '. The highlighted source is what the next instruction came from.';
    }
    btn(row, 'Step', function () { stop(); if (vm) { vm.step(); draw(); } }, 'primary');
    var runB = btn(row, 'Run', function () { if (timer) { stop(); return; } if (!vm || vm.done) reset(); if (!vm) return; runB.textContent = 'Pause'; timer = setInterval(function () { if (!vm.step() || vm.steps > 20000) { stop(); } draw(); }, 140); });
    btn(row, 'Reset', reset);
    ed.addEventListener('input', reset); reset();
  };

  // ---------------------------------------------------------------- tests, and a program that games them
  F.tests = function (fig) {
    var row = el('div', 'lab-row'), ed = editor(fig, GCD_FN), out = el('div', 'tgrid'), sum = el('p', 'lab-sum');
    fig.insertBefore(row, ed); fig.appendChild(out); fig.appendChild(sum);
    var VIS = [[48, 18, 6], [17, 5, 1], [0, 9, 9], [12, 12, 12], [100, 75, 25]], HID = [[21, 14, 7], [9, 28, 1], [1071, 462, 21], [5, 0, 5], [64, 48, 16]];
    var P = [['Correct', GCD_FN], ['Off by one', GCD_FN.replace('b != 0', 'b > 1')], ['Wrong operator', GCD_FN.replace('a % b', 'a - b')],
      ['Memorize the visible tests', "fn gcd(a, b) {\n  if a == 48 { return 6 }\n  if a == 17 { return 1 }\n  if a == 0 { return 9 }\n  if a == 12 { return 12 }\n  return 25\n}\n"]];
    P.forEach(function (p) { btn(row, p[0], function () { ed.value = p[1]; draw(); }); });
    function table(title, tests, built) {
      var pass = 0, rows = tests.map(function (t) {
        var r = M.callFn(built, 'gcd', [t[0], t[1]], 4000), ok = !r.error && r.value === t[2]; if (ok) pass++;
        return '<tr class="' + (ok ? 'ok' : 'no') + '"><td>gcd(' + t[0] + ', ' + t[1] + ')</td><td>' + t[2] + '</td><td>' + (r.error ? (r.error.timeout ? 'never finished' : esc(r.error.msg)) : esc(String(r.value === null ? 'nothing' : r.value))) + '</td><td>' + (ok ? 'pass' : 'fail') + '</td></tr>';
      }).join('');
      return { html: '<div><h4>' + title + ' <b>' + pass + '/' + tests.length + '</b></h4><table class="tt"><thead><tr><th>call</th><th>expected</th><th>got</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>', pass: pass };
    }
    function draw() {
      var built = safe(function () { return M.build(ed.value); }, ed.value, out); if (!built) { sum.textContent = 'The program does not even start, so every test fails.'; return; }
      var a = table('Tests the author can see', VIS, built), b = table('Held-out tests', HID, built);
      out.innerHTML = a.html + b.html;
      sum.innerHTML = a.pass === 5 && b.pass === 5 ? 'All ten pass. That is evidence, not proof: there are infinitely many inputs and ten were tried.' :
        a.pass === 5 ? '<b>Every visible test passes and the program is wrong.</b> A reward built only on the visible tests would call this a success.' :
        'Reward = ' + a.pass + '/5 on the visible tests. In training, this number is the whole signal the model gets.';
    }
    ed.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- proof: checking every case up to N versus a proof for all N
  F.proof = function (fig) {
    var ctl = el('div', 'ctl', '<label>Check every pair up to <b class="pv">40</b></label>'), rng = el('input'); rng.type = 'range'; rng.min = 8; rng.max = 120; rng.value = 40; ctl.appendChild(rng);
    var cv = el('canvas', 'pgrid'), sum = el('p', 'lab-sum'); cv.setAttribute('role', 'img'); cv.setAttribute('aria-label', 'Grid of pairs, colored where the two numbers share no factor');
    fig.appendChild(ctl); fig.appendChild(cv); fig.appendChild(sum);
    function g(a, b) { while (b !== 0) { var t = a % b; a = b; b = t; } return a; }
    function draw() {
      var N = +rng.value, px = Math.max(2, Math.floor(480 / N)), ok = 0, cop = 0; cv.width = cv.height = N * px;
      var cx = cv.getContext('2d'), on = css('--accent'), off = css('--rule');
      for (var a = 1; a <= N; a++) for (var b = 1; b <= N; b++) {
        var d = g(a, b), good = a % d === 0 && b % d === 0;
        if (good) for (var k = d + 1; k <= Math.min(a, b); k++) if (a % k === 0 && b % k === 0) { good = false; break; }
        if (good) ok++; if (d === 1) cop++;
        cx.fillStyle = d === 1 ? on : off; cx.fillRect((a - 1) * px, (N - b) * px, px - (px > 3 ? 1 : 0), px - (px > 3 ? 1 : 0));
      }
      ctl.querySelector('.pv').textContent = N;
      sum.innerHTML = 'Checked all ' + (N * N).toLocaleString('en-US') + ' pairs up to ' + N + ': the loop returned the true greatest common divisor in ' + ok.toLocaleString('en-US') + ' of them. ' +
        'Colored squares are pairs with no common factor: ' + (100 * cop / (N * N)).toFixed(1) + '% here, and the share tends to 6/π² ≈ 60.8% as the grid grows. However far you drag, infinitely many pairs stay unchecked.';
    }
    rng.addEventListener('input', draw); redraws.push(draw); draw();
  };

  // ---------------------------------------------------------------- change: a line diff
  function diffLines(a, b) {
    var n = a.length, m = b.length, L = [], i, j;
    for (i = 0; i <= n; i++) { L.push(new Array(m + 1).fill(0)); }
    for (i = n - 1; i >= 0; i--) for (j = m - 1; j >= 0; j--) L[i][j] = a[i] === b[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1]);
    var out = []; i = 0; j = 0;
    while (i < n && j < m) { if (a[i] === b[j]) { out.push([' ', a[i]]); i++; j++; } else if (L[i + 1][j] >= L[i][j + 1]) out.push(['-', a[i++]]); else out.push(['+', b[j++]]); }
    while (i < n) out.push(['-', a[i++]]); while (j < m) out.push(['+', b[j++]]);
    return out;
  }
  F.diff = function (fig) {
    var two = el('div', 'two'), A = el('div'), B = el('div'); two.appendChild(A); two.appendChild(B); fig.appendChild(two);
    A.appendChild(el('h4', '', 'Before')); B.appendChild(el('h4', '', 'After'));
    var ea = editor(A, "fn gcd(a, b) {\n  while a != b {\n    if a > b {\n      a = a - b\n    } else {\n      b = b - a\n    }\n  }\n  return a\n}\n"), eb = editor(B, GCD_FN, 10);
    var out = el('pre', 'diffout'), sum = el('p', 'lab-sum'); fig.appendChild(out); fig.appendChild(sum);
    function behave(src) { try { var b = M.build(src); var r = M.callFn(b, 'gcd', [48, 18], 4000); return r.error ? (r.error.timeout ? 'never finishes' : 'fails') : 'gives ' + r.value + ' in ' + r.steps + ' steps'; } catch (e) { return 'does not start'; } }
    function draw() {
      var d = diffLines(ea.value.replace(/\n$/, '').split('\n'), eb.value.replace(/\n$/, '').split('\n')), add = 0, del = 0;
      out.innerHTML = d.map(function (x) { if (x[0] === '+') add++; if (x[0] === '-') del++; return '<span class="d' + (x[0] === '+' ? 'a' : x[0] === '-' ? 'd' : 'k') + '">' + x[0] + ' ' + esc(x[1]) + '</span>'; }).join('\n');
      sum.innerHTML = '<b>+' + add + ' −' + del + '</b> lines. For gcd(48, 18) the old version ' + behave(ea.value) + ' and the new one ' + behave(eb.value) + '. The diff shows what changed in the text. Whether the behavior changed is a separate question, and the harder one.';
    }
    ea.addEventListener('input', draw); eb.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- physics: four transistors make a NAND
  F.nand = function (fig) {
    var st = { a: 1, b: 0 }, box = el('div', 'nandbox'), sum = el('p', 'lab-sum'); fig.appendChild(box); fig.appendChild(sum);
    function sw(x, y, on, name, note) {
      return '<g class="sw ' + (on ? 'on' : 'off') + '"><line x1="' + x + '" y1="' + (y - 26) + '" x2="' + x + '" y2="' + (y - 9) + '"/><line x1="' + x + '" y1="' + (y + 9) + '" x2="' + x + '" y2="' + (y + 26) + '"/>' +
        (on ? '<line x1="' + x + '" y1="' + (y - 9) + '" x2="' + x + '" y2="' + (y + 9) + '"/>' : '<line x1="' + x + '" y1="' + (y - 9) + '" x2="' + (x + 11) + '" y2="' + (y + 6) + '"/>') +
        '<circle cx="' + x + '" cy="' + (y - 9) + '" r="2.6"/><circle cx="' + x + '" cy="' + (y + 9) + '" r="2.6"/><text x="' + (x + 18) + '" y="' + (y - 2) + '" class="nm">' + name + '</text><text x="' + (x + 18) + '" y="' + (y + 12) + '" class="nt">' + note + '</text></g>';
    }
    function draw() {
      var a = st.a, b = st.b, out = (a && b) ? 0 : 1;
      var s = '<svg viewBox="0 0 560 330" role="img" aria-label="CMOS NAND gate drawn as four switches">';
      s += '<line x1="60" y1="30" x2="400" y2="30" class="rail hi"/><text x="410" y="34" class="nm">supply (1)</text><line x1="60" y1="300" x2="400" y2="300" class="rail lo"/><text x="410" y="304" class="nm">ground (0)</text>';
      s += '<line x1="140" y1="30" x2="140" y2="54" class="w"/><line x1="290" y1="30" x2="290" y2="54" class="w"/>' + sw(140, 80, !a, 'P1', 'closes when A = 0') + sw(290, 80, !b, 'P2', 'closes when B = 0');
      s += '<line x1="140" y1="106" x2="140" y2="130" class="w"/><line x1="290" y1="106" x2="290" y2="130" class="w"/><line x1="140" y1="130" x2="290" y2="130" class="w"/><line x1="215" y1="130" x2="215" y2="154" class="w"/>';
      s += '<line x1="215" y1="142" x2="470" y2="142" class="w ' + (out ? 'hi' : 'lo') + '"/><circle cx="215" cy="142" r="3.4" class="dot"/><text x="476" y="138" class="nm">output</text><text x="476" y="160" class="big ' + (out ? 'hi' : 'lo') + '">' + out + '</text>';
      s += sw(215, 180, !!a, 'N1', 'closes when A = 1') + '<line x1="215" y1="206" x2="215" y2="224" class="w"/>' + sw(215, 250, !!b, 'N2', 'closes when B = 1') + '<line x1="215" y1="276" x2="215" y2="300" class="w"/>';
      s += '</svg>';
      var tt = '<table class="tt nandtt"><thead><tr><th>A</th><th>B</th><th>NAND</th></tr></thead><tbody>' + [[0, 0], [0, 1], [1, 0], [1, 1]].map(function (r) { return '<tr class="' + (r[0] === a && r[1] === b ? 'cur' : '') + '"><td>' + r[0] + '</td><td>' + r[1] + '</td><td>' + ((r[0] && r[1]) ? 0 : 1) + '</td></tr>'; }).join('') + '</tbody></table>';
      box.innerHTML = '<div class="nandctl"><button type="button" class="bit ' + (a ? 'on' : '') + '" data-k="a" aria-pressed="' + !!a + '">A = ' + a + '</button><button type="button" class="bit ' + (b ? 'on' : '') + '" data-k="b" aria-pressed="' + !!b + '">B = ' + b + '</button>' + tt + '</div>' + s;
      box.querySelectorAll('.bit').forEach(function (x) { x.addEventListener('click', function () { st[x.dataset.k] = st[x.dataset.k] ? 0 : 1; draw(); }); });
      sum.textContent = out ? 'At least one upper switch is closed and the path to ground is broken, so the output is pulled up to 1.' : 'Both lower switches are closed and both upper ones are open, so the output is pulled down to 0.';
    }
    draw();
  };

  // ---------------------------------------------------------------- gates: an 8-bit adder, carry by carry
  F.adder = function (fig) {
    var A = 100, B = 58, box = el('div', 'adder'), sum = el('p', 'lab-sum'); fig.appendChild(box); fig.appendChild(sum);
    function draw() {
      var c = 0, cols = '', carries = 0;
      var bits = [];
      for (var i = 0; i < 8; i++) { var a = (A >> i) & 1, b = (B >> i) & 1, s = a ^ b ^ c, co = (a & b) | (c & (a ^ b)); bits.push({ a: a, b: b, cin: c, s: s, co: co }); if (co) carries++; c = co; }
      for (var j = 7; j >= 0; j--) {
        var t = bits[j];
        cols += '<div class="acol"><span class="pw">' + (1 << j) + '</span><button type="button" class="bit ' + (t.a ? 'on' : '') + '" data-w="A" data-i="' + j + '" aria-label="A bit ' + j + '">' + t.a + '</button><button type="button" class="bit ' + (t.b ? 'on' : '') + '" data-w="B" data-i="' + j + '" aria-label="B bit ' + j + '">' + t.b + '</button>' +
          '<span class="fa' + (t.co ? ' carry' : '') + '"><i>carry in ' + t.cin + '</i>full adder<i>carry out ' + t.co + '</i></span><span class="bit out ' + (t.s ? 'on' : '') + '">' + t.s + '</span></div>';
      }
      var total = A + B, shown = total & 255;
      box.innerHTML = '<div class="alabels"><span></span><span>A = ' + A + '</span><span>B = ' + B + '</span><span></span><span>sum = ' + shown + '</span></div><div class="acols">' + cols + '</div>';
      box.querySelectorAll('button.bit').forEach(function (x) { x.addEventListener('click', function () { var m = 1 << +x.dataset.i; if (x.dataset.w === 'A') A ^= m; else B ^= m; draw(); }); });
      sum.innerHTML = A + ' + ' + B + ' = ' + total + (total > 255 ? '. Eight bits can only hold up to 255, so the machine reports <b>' + shown + '</b> and raises a carry flag. This is integer overflow.' : '.') +
        ' ' + carries + ' of the 8 stages passed a carry to the next. Built from NAND gates alone this adder takes 72 gates, about 288 transistors.';
    }
    draw();
  };

  // ---------------------------------------------------------------- machine: fetch, decode, execute
  F.cpu = function (fig) {
    var PROG = [['CMP', 0, 1, 'compare r0 with r1, remember the result in the flags'], ['BEQ', 14, null, 'if they were equal, jump to address 14'], ['BLT', 10, null, 'if r0 was smaller, jump to address 10'], ['SUB', 0, 1, 'r0 = r0 - r1'], ['JMP', 0, null, 'jump back to address 0'], ['SUB', 1, 0, 'r1 = r1 - r0'], ['JMP', 0, null, 'jump back to address 0'], ['HALT', null, null, 'stop']];
    var OPC = { CMP: 0x10, SUB: 0x20, BEQ: 0x30, BLT: 0x31, JMP: 0x32, HALT: 0xFF };
    var mem = []; PROG.forEach(function (p) { mem.push(OPC[p[0]]); mem.push(p[0] === 'CMP' || p[0] === 'SUB' ? (p[1] << 4) | p[2] : p[0] === 'HALT' ? 0 : p[1]); });
    function hx(b) { return (b < 16 ? '0' : '') + b.toString(16).toUpperCase(); }
    var row = el('div', 'lab-row'), ia = el('input', 'lab-num'), ib = el('input', 'lab-num'); [ia, ib].forEach(function (x, i) { x.type = 'number'; x.min = 1; x.max = 255; x.value = i ? 18 : 48; x.setAttribute('aria-label', 'Starting value of register ' + i); });
    row.appendChild(el('span', 'lab-lbl', 'r0 =')); row.appendChild(ia); row.appendChild(el('span', 'lab-lbl', 'r1 =')); row.appendChild(ib);
    var grid = el('div', 'cpugrid'), sum = el('p', 'lab-sum'); fig.appendChild(row); fig.appendChild(grid); fig.appendChild(sum);
    var s, timer = null;
    function clamp(v) { v = Math.floor(+v) || 1; return Math.max(1, Math.min(255, v)); }
    function reset() { stop(); s = { r: [clamp(ia.value), clamp(ib.value)], pc: 0, z: 0, n: 0, halt: false, steps: 0 }; draw(); }
    function stop() { if (timer) { clearInterval(timer); timer = null; runB.textContent = 'Run'; } }
    function step() {
      if (s.halt) return false; var op = mem[s.pc], arg = mem[s.pc + 1]; s.steps++; var next = s.pc + 2;
      if (op === 0x10) { var d = s.r[arg >> 4] - s.r[arg & 15]; s.z = d === 0 ? 1 : 0; s.n = d < 0 ? 1 : 0; }
      else if (op === 0x20) { s.r[arg >> 4] = (s.r[arg >> 4] - s.r[arg & 15]) & 255; }
      else if (op === 0x30) { if (s.z) next = arg; } else if (op === 0x31) { if (s.n) next = arg; } else if (op === 0x32) next = arg;
      else if (op === 0xFF) { s.halt = true; return false; }
      s.pc = next; return true;
    }
    function draw() {
      var cur = s.pc / 2, p = PROG[cur];
      var asm = PROG.map(function (q, i) { return '<li' + (i === cur ? ' class="pc"' : '') + '><i>' + hx(i * 2) + '</i><span class="hexb">' + hx(mem[i * 2]) + ' ' + hx(mem[i * 2 + 1]) + '</span>' + q[0] + (q[0] === 'CMP' || q[0] === 'SUB' ? ' r' + q[1] + ', r' + q[2] : q[0] === 'HALT' ? '' : ' ' + hx(q[1])) + '</li>'; }).join('');
      grid.innerHTML = '<div class="expane"><h4>Memory: address, bytes, meaning</h4><ol class="exins cpu">' + asm + '</ol></div>' +
        '<div class="expane"><h4>Registers</h4><div class="cells"><span class="cellv"><i>r0</i>' + s.r[0] + '</span><span class="cellv"><i>r1</i>' + s.r[1] + '</span><span class="cellv"><i>pc</i>' + hx(s.pc) + '</span></div>' +
        '<h4>Flags from the last compare</h4><div class="cells"><span class="cellv"><i>equal</i>' + s.z + '</span><span class="cellv"><i>less</i>' + s.n + '</span></div>' +
        '<h4>The processor is about to</h4><p>' + (s.halt ? 'Nothing. It has stopped.' : '<b>fetch</b> the two bytes at address ' + hx(s.pc) + ', <b>decode</b> them as ' + p[0] + ', and <b>execute</b>: ' + p[3] + '.') + '</p></div>';
      sum.textContent = s.halt ? 'Halted after ' + s.steps + ' instructions with r0 = ' + s.r[0] + ', the greatest common divisor. The same eight instructions work for any two starting numbers.' : 'Instruction ' + s.steps + '. The program is the 16 bytes on the left. Nothing else tells the machine what to do.';
    }
    btn(row, 'Step', function () { stop(); step(); draw(); }, 'primary');
    var runB = btn(row, 'Run', function () { if (timer) { stop(); return; } if (s.halt) reset(); runB.textContent = 'Pause'; timer = setInterval(function () { if (!step()) stop(); draw(); }, 220); });
    btn(row, 'Reset', reset);
    ia.addEventListener('change', reset); ib.addEventListener('change', reset); reset();
  };

  // ---------------------------------------------------------------- os: one processor, three programs
  F.sched = function (fig) {
    var ctl = el('div', 'ctl', '<label>Time slice: <b class="qv">2</b> units</label>'), rng = el('input'); rng.type = 'range'; rng.min = 1; rng.max = 10; rng.value = 2; ctl.appendChild(rng);
    var out = el('div', 'sched'), sum = el('p', 'lab-sum'); fig.appendChild(ctl); fig.appendChild(out); fig.appendChild(sum);
    var JOBS = [['Download', 9], ['Editor', 6], ['Music', 3]];
    function draw() {
      var q = +rng.value, left = JOBS.map(function (j) { return j[1]; }), t = 0, segs = [], fin = [0, 0, 0], first = [-1, -1, -1], sw = 0, last = -1, queue = [0, 1, 2];
      while (queue.length) { var i = queue.shift(), run = Math.min(q, left[i]); if (last !== -1 && last !== i) sw++; if (first[i] < 0) first[i] = t; segs.push([i, t, run]); t += run; left[i] -= run; last = i; if (left[i] > 0) queue.push(i); else fin[i] = t; }
      var W = 600, u = (W - 110) / t, s = '<svg viewBox="0 0 ' + W + ' 150" role="img" aria-label="Timeline of which program runs when">';
      JOBS.forEach(function (j, k) { s += '<text x="0" y="' + (28 + k * 36) + '" class="nm">' + j[0] + '</text><line x1="100" y1="' + (24 + k * 36) + '" x2="' + (W - 10) + '" y2="' + (24 + k * 36) + '" class="lane"/>'; });
      segs.forEach(function (g) { s += '<rect x="' + (100 + g[1] * u) + '" y="' + (12 + g[0] * 36) + '" width="' + Math.max(1, g[2] * u - 2) + '" height="24" rx="5" class="job j' + g[0] + '"/>'; });
      for (var x = 0; x <= t; x += (t > 12 ? 3 : 1)) s += '<text x="' + (100 + x * u) + '" y="138" class="nt" text-anchor="middle">' + x + '</text>';
      s += '</svg>'; out.innerHTML = s; ctl.querySelector('.qv').textContent = q;
      sum.innerHTML = 'One processor, ' + sw + ' switches between programs. Music, the shortest job (3 units of work), first gets to run at time <b>' + first[2] + '</b> and is done at <b>' + fin[2] + '</b>. With a long slice it waits behind the long jobs; with a short slice every program gets a turn early, at the price of more switching.';
    }
    rng.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- compilers: same meaning, fewer instructions
  F.compile = function (fig) {
    var ed = editor(fig, "seconds = 60 * 60 * 24\nweek = seconds * 7\nprint(week + 2 * (10 - 4))\n"), two = el('div', 'two'), sum = el('p', 'lab-sum'); fig.appendChild(two); fig.appendChild(sum);
    function side(title, b) { var c = b.code['(top level)'].code; return { html: '<div><h4>' + title + ' <b>' + c.length + '</b></h4><ol class="exins">' + c.map(function (x, i) { return '<li><i>' + i + '</i>' + esc(M.fmtIns(x)) + '</li>'; }).join('') + '</ol></div>', n: c.length }; }
    function draw() {
      var r = safe(function () {
        var a = M.build(ed.value), b = M.build(ed.value, { fold: true }), va = new M.VM(a.code).run(50000), vb = new M.VM(b.code).run(50000);
        return { a: side('Translated as written', a), b: side('After folding constants', b), sa: va.steps, sb: vb.steps, oa: va.out.join(', '), ob: vb.out.join(', ') };
      }, ed.value, two); if (!r) { sum.textContent = ''; return; }
      two.innerHTML = r.a.html + r.b.html;
      sum.innerHTML = 'Both versions print <b>' + esc(r.oa || 'nothing') + '</b>' + (r.oa === r.ob ? '' : ' (and ' + esc(r.ob) + ', which would be a compiler bug)') + '. The first takes ' + r.sa + ' steps, the second ' + r.sb + '. The compiler did the arithmetic once, so the machine never has to.';
    }
    ed.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- languages: one algorithm, two notations
  F.langs = function (fig) {
    var d = document.getElementById('langdata'); if (!d) return; var L = JSON.parse(d.textContent), ids = Object.keys(L);
    var row = el('div', 'lab-row'), two = el('div', 'two'); fig.appendChild(row); fig.appendChild(two);
    function sel(def) { var s = el('select', 'f'); s.setAttribute('aria-label', 'Language'); ids.forEach(function (i) { var o = el('option', '', esc(L[i].name)); o.value = i; s.appendChild(o); }); s.value = L[def] ? def : ids[0]; row.appendChild(s); return s; }
    var a = sel(fig.dataset.a || 'c'), b = sel(fig.dataset.b || 'python');
    function pane(i) { var x = L[i]; return '<div><h4><a href="/languages/' + i + '/">' + esc(x.name) + '</a> <b>' + x.year + '</b></h4><div class="codebox"><pre>' + esc(x.code) + '</pre></div><p class="lab-dim">' + esc(x.runs) + '</p></div>'; }
    function draw() { two.innerHTML = pane(a.value) + pane(b.value); }
    a.addEventListener('change', draw); b.addEventListener('change', draw); draw();
  };

  // ---------------------------------------------------------------- applications: a spreadsheet is a program
  F.sheet = function (fig) {
    var COLS = 'ABCD', ROWS = 5;
    var cells = { A1: 'Item', B1: 'Price', C1: 'Count', D1: 'Total', A2: 'Paper', B2: '4', C2: '10', D2: '=B2*C2', A3: 'Ink', B3: '12', C3: '3', D3: '=B3*C3', A4: 'Stamps', B4: '2', C4: '20', D4: '=B4*C4', A5: 'Sum', D5: '=SUM(D2:D4)' };
    var box = el('div', 'sheet'), sum = el('p', 'lab-sum'); fig.appendChild(box); fig.appendChild(sum);
    function evalCell(id, seen) {
      var raw = (cells[id] || '').trim(); if (raw === '') return 0;
      if (raw[0] !== '=') { var v = Number(raw); return isNaN(v) ? raw : v; }
      if (seen[id]) throw new Error('circular'); seen[id] = 1;
      var src = raw.slice(1).toUpperCase().replace(/\s+/g, ''), p = 0;
      function ref(r) { var v = evalCell(r, seen); if (typeof v !== 'number') throw new Error('text'); return v; }
      function prim() {
        var m;
        if ((m = /^SUM\(([A-D][1-5]):([A-D][1-5])\)/.exec(src.slice(p)))) { p += m[0].length; var t = 0; for (var c = COLS.indexOf(m[1][0]); c <= COLS.indexOf(m[2][0]); c++) for (var r = +m[1][1]; r <= +m[2][1]; r++) t += ref(COLS[c] + r); return t; }
        if ((m = /^[A-D][1-5]/.exec(src.slice(p)))) { p += 2; return ref(m[0]); }
        if ((m = /^\d+(\.\d+)?/.exec(src.slice(p)))) { p += m[0].length; return parseFloat(m[0]); }
        if (src[p] === '(') { p++; var v = add(); if (src[p] !== ')') throw new Error('syntax'); p++; return v; }
        if (src[p] === '-') { p++; return -prim(); }
        throw new Error('syntax');
      }
      function mul() { var v = prim(); while (src[p] === '*' || src[p] === '/') { var o = src[p++], r = prim(); v = o === '*' ? v * r : v / r; } return v; }
      function add() { var v = mul(); while (src[p] === '+' || src[p] === '-') { var o = src[p++], r = mul(); v = o === '+' ? v + r : v - r; } return v; }
      var out = add(); if (p < src.length) throw new Error('syntax'); delete seen[id]; return out;
    }
    function show(id) { try { var v = evalCell(id, {}); return typeof v === 'number' ? String(Math.round(v * 100) / 100) : v; } catch (e2) { return e2.message === 'circular' ? '#LOOP' : e2.message === 'text' ? '#TEXT' : '#ERROR'; } }
    var focus = null;
    function draw() {
      var h = '<table><thead><tr><th></th>' + COLS.split('').map(function (c) { return '<th>' + c + '</th>'; }).join('') + '</tr></thead><tbody>', nf = 0;
      for (var r = 1; r <= ROWS; r++) { h += '<tr><th>' + r + '</th>'; for (var c = 0; c < 4; c++) { var id = COLS[c] + r, raw = cells[id] || '', isF = raw[0] === '='; if (isF) nf++; h += '<td class="' + (isF ? 'fx' : '') + '"><input data-id="' + id + '" aria-label="Cell ' + id + '" value="' + esc(focus === id ? raw : show(id)) + '" spellcheck="false"></td>'; } h += '</tr>'; }
      box.innerHTML = h + '</tbody></table>';
      box.querySelectorAll('input').forEach(function (inp) {
        inp.addEventListener('focus', function () { focus = inp.dataset.id; inp.value = cells[focus] || ''; });
        inp.addEventListener('input', function () { cells[inp.dataset.id] = inp.value; refresh(inp.dataset.id); });
        inp.addEventListener('blur', function () { focus = null; inp.value = show(inp.dataset.id); });
        inp.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') inp.blur(); });
      });
      note(nf);
    }
    function refresh(skip) { var nf = 0; box.querySelectorAll('input').forEach(function (inp) { var id = inp.dataset.id, raw = cells[id] || ''; if (raw[0] === '=') nf++; inp.parentNode.className = raw[0] === '=' ? 'fx' : ''; if (id !== skip) inp.value = show(id); }); note(nf); }
    function note(nf) { sum.innerHTML = 'The ' + nf + ' tinted cells hold formulas. Click one to read it, or change any price and watch the rest recompute. Nothing here says <i>in what order</i> to calculate: you state what each cell is, and the spreadsheet works out the order.'; }
    draw();
  };

  // ---------------------------------------------------------------- networks: a message gets wrapped four times
  F.packet = function (fig) {
    var ctl = el('div', 'ctl', '<label>Message size: <b class="mv"></b></label>'), rng = el('input'); rng.type = 'range'; rng.min = 0; rng.max = 60; rng.value = 14; ctl.appendChild(rng);
    var out = el('div', 'pkt'), sum = el('p', 'lab-sum'); fig.appendChild(ctl); fig.appendChild(out); fig.appendChild(sum);
    function nice(n) { return n >= 1048576 ? (n / 1048576).toFixed(1) + ' MB' : n >= 1024 ? (n / 1024).toFixed(1) + ' kB' : n + ' bytes'; }
    function draw() {
      var size = Math.round(Math.pow(10, +rng.value / 10)), MSS = 1460, n = Math.ceil(size / MSS), first = Math.min(size, MSS), wire = size + n * 58;
      ctl.querySelector('.mv').textContent = nice(size);
      out.innerHTML = '<div class="lay l4"><span>Ethernet frame <i>14 bytes in front, 4 behind: which device on this link</i></span><div class="lay l3"><span>IP packet <i>20 bytes: which machine on the internet</i></span><div class="lay l2"><span>TCP segment <i>20 bytes: which program, which position in the stream</i></span><div class="lay l1"><span>Your data <i>' + nice(first) + (n > 1 ? ' of ' + nice(size) : '') + '</i></span></div></div></div></div>';
      sum.innerHTML = nice(size) + ' of data travels as <b>' + n.toLocaleString('en-US') + ' packet' + (n === 1 ? '' : 's') + '</b>, ' + nice(wire) + ' on the wire (' + (100 * (wire - size) / wire).toFixed(wire - size > wire / 10 ? 0 : 1) + '% is headers and trailer; very small frames are also padded up to 64 bytes). Each layer reads only its own header and treats everything inside as opaque cargo. Figures assume the smallest headers on Ethernet with IPv4; real traffic adds options and encryption.';
    }
    rng.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- learned programs: 17 numbers that nobody wrote
  F.xor = function (fig) {
    var TARGETS = { XOR: [0, 1, 1, 0], AND: [0, 0, 0, 1], OR: [0, 1, 1, 1], NAND: [1, 1, 1, 0] }, X = [[0, 0], [0, 1], [1, 0], [1, 1]], Hn = 4;
    var row = el('div', 'lab-row'), sel = el('select', 'f'); sel.setAttribute('aria-label', 'Function to learn'); Object.keys(TARGETS).forEach(function (k) { var o = el('option', '', k); o.value = k; sel.appendChild(o); }); row.appendChild(el('span', 'lab-lbl', 'Learn')); row.appendChild(sel);
    var two = el('div', 'xorgrid'), cv = el('canvas', 'xorcv'); cv.width = cv.height = 220; cv.setAttribute('role', 'img'); cv.setAttribute('aria-label', 'Output of the network for every pair of inputs between 0 and 1');
    var side = el('div', 'xorside'), sum = el('p', 'lab-sum'); two.appendChild(cv); two.appendChild(side); fig.appendChild(row); fig.appendChild(two); fig.appendChild(sum);
    var seed = 7, w, steps, timer = null;
    function rnd() { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296 * 2 - 1; }
    function init() { w = { w1: [], b1: [], w2: [], b2: 0 }; for (var i = 0; i < Hn; i++) { w.w1.push([rnd(), rnd()]); w.b1.push(rnd() * 0.5); w.w2.push(rnd()); } steps = 0; }
    function fwd(x) { var h = [], z = w.b2; for (var i = 0; i < Hn; i++) { h.push(Math.tanh(w.w1[i][0] * x[0] + w.w1[i][1] * x[1] + w.b1[i])); z += w.w2[i] * h[i]; } return { h: h, y: 1 / (1 + Math.exp(-z)) }; }
    function train(k) {
      var T = TARGETS[sel.value], lr = 0.5;
      for (var s = 0; s < k; s++) {
        var g1 = [], gb1 = [], g2 = [], gb2 = 0, i; for (i = 0; i < Hn; i++) { g1.push([0, 0]); gb1.push(0); g2.push(0); }
        X.forEach(function (x, n) { var f = fwd(x), d = f.y - T[n]; gb2 += d; for (var j = 0; j < Hn; j++) { g2[j] += d * f.h[j]; var dh = d * w.w2[j] * (1 - f.h[j] * f.h[j]); g1[j][0] += dh * x[0]; g1[j][1] += dh * x[1]; gb1[j] += dh; } });
        for (i = 0; i < Hn; i++) { w.w2[i] -= lr * g2[i] / 4; w.b1[i] -= lr * gb1[i] / 4; w.w1[i][0] -= lr * g1[i][0] / 4; w.w1[i][1] -= lr * g1[i][1] / 4; }
        w.b2 -= lr * gb2 / 4; steps++;
      }
    }
    function mix(a, b, t) { return 'rgb(' + [0, 1, 2].map(function (i) { return Math.round(a[i] + (b[i] - a[i]) * t); }).join(',') + ')'; }
    function rgb(v) { var m = /^#(..)(..)(..)$/.exec(v); return m ? [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)] : [128, 128, 128]; }
    function draw() {
      var cx = cv.getContext('2d'), N = 44, c0 = rgb(css('--paper-deep')), c1 = rgb(css('--accent')), px = cv.width / N, T = TARGETS[sel.value], loss = 0, right = 0;
      for (var i = 0; i < N; i++) for (var j = 0; j < N; j++) { cx.fillStyle = mix(c0, c1, fwd([(i + .5) / N, 1 - (j + .5) / N]).y); cx.fillRect(i * px, j * px, px + 1, px + 1); }
      var rows = X.map(function (x, n) { var y = fwd(x).y; loss -= T[n] ? Math.log(Math.max(y, 1e-9)) : Math.log(Math.max(1 - y, 1e-9)); if ((y > .5 ? 1 : 0) === T[n]) right++; return '<tr class="' + ((y > .5 ? 1 : 0) === T[n] ? 'ok' : 'no') + '"><td>' + x[0] + ', ' + x[1] + '</td><td>' + T[n] + '</td><td>' + y.toFixed(2) + '</td></tr>'; }).join('');
      var nums = []; w.w1.forEach(function (p) { nums.push(p[0], p[1]); }); nums = nums.concat(w.b1, w.w2, [w.b2]);
      side.innerHTML = '<table class="tt"><thead><tr><th>inputs</th><th>wanted</th><th>network says</th></tr></thead><tbody>' + rows + '</tbody></table><h4>The whole program</h4><p class="wts">' + nums.map(function (v) { return '<span>' + (v >= 0 ? '+' : '') + v.toFixed(2) + '</span>'; }).join('') + '</p>';
      sum.innerHTML = 'Step ' + steps + ', error ' + (loss / 4).toFixed(3) + ', ' + right + ' of 4 right. ' + (right === 4 && steps > 0 ? 'Those 17 numbers now compute ' + sel.value + '. Nobody typed them; a loop adjusted them until the answers came out right, and no line among them says how.' : 'The numbers start out random. Press Train and they are nudged, a little at a time, toward giving the wanted answers.');
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; tb2.textContent = 'Train'; } }
    var tb2 = btn(row, 'Train', function () { if (timer) { stop(); return; } tb2.textContent = 'Pause'; timer = setInterval(function () { train(25); draw(); if (steps >= 6000) stop(); }, 40); }, 'primary');
    btn(row, 'New random start', function () { stop(); init(); draw(); });
    sel.addEventListener('change', function () { stop(); init(); draw(); });
    redraws.push(draw); init(); draw();
  };

  // ---------------------------------------------------------------- computation: one-line rules, endless behavior
  F.ca = function (fig) {
    var row = el('div', 'lab-row'), inp = el('input', 'lab-num'); inp.type = 'number'; inp.min = 0; inp.max = 255; inp.value = 110; inp.setAttribute('aria-label', 'Rule number, 0 to 255');
    row.appendChild(el('span', 'lab-lbl', 'Rule')); row.appendChild(inp); [110, 30, 90, 184, 250].forEach(function (r) { btn(row, String(r), function () { inp.value = r; draw(); }, 'mono'); });
    var rule = el('div', 'rulebox'), cv = el('canvas', 'cacv'), sum = el('p', 'lab-sum'); cv.setAttribute('role', 'img'); cv.setAttribute('aria-label', 'Rows of cells, each computed from the row above');
    fig.appendChild(row); fig.appendChild(rule); fig.appendChild(cv); fig.appendChild(sum);
    var NOTE = { 110: 'Rule 110 can carry out any computation, given a suitable starting row of unlimited length. Matthew Cook proved it; the proof was published in 2004.', 30: 'Rule 30 looks random down its center column, and has been used as a random number generator.', 90: 'Rule 90 draws the Sierpinski triangle from a single cell: each cell is the exclusive-or of its two neighbors. (The row here wraps around, so the pattern distorts once it reaches the edge.)', 184: 'Rule 184 is a traffic model: a car moves right when the cell ahead is free.', 250: 'Rule 250 turns each cell on when either neighbor was on, which draws a plain alternating pattern.' };
    function draw() {
      var R = Math.max(0, Math.min(255, Math.floor(+inp.value) || 0)), W = 181, H = 110, px = 4; cv.width = W * px; cv.height = H * px;
      var cx = cv.getContext('2d'), on = css('--ink'), row0 = new Uint8Array(W), i, t; row0[R === 110 ? W - 2 : (W >> 1)] = 1; if (R === 184) for (i = 0; i < W; i++) row0[i] = ((i * 7919) % 13) < 5 ? 1 : 0;
      cx.clearRect(0, 0, cv.width, cv.height); cx.fillStyle = on;
      for (t = 0; t < H; t++) { var nx = new Uint8Array(W); for (i = 0; i < W; i++) { if (row0[i]) cx.fillRect(i * px, t * px, px, px); var k = (row0[(i + W - 1) % W] << 2) | (row0[i] << 1) | row0[(i + 1) % W]; nx[i] = (R >> k) & 1; } row0 = nx; }
      var h = ''; for (var p = 7; p >= 0; p--) h += '<span class="rb"><i class="' + ((p >> 2) & 1 ? 'on' : '') + '"></i><i class="' + ((p >> 1) & 1 ? 'on' : '') + '"></i><i class="' + (p & 1 ? 'on' : '') + '"></i><b class="' + ((R >> p) & 1 ? 'on' : '') + '"></b></span>';
      rule.innerHTML = h;
      sum.textContent = 'The whole program is the eight small pictures above: for each pattern of three cells, what the cell below becomes. ' + (NOTE[R] || 'There are only 256 such rules.');
    }
    inp.addEventListener('input', draw); redraws.push(draw); draw();
  };
  F.collatz = function (fig) {
    var row = el('div', 'lab-row'), inp = el('input', 'lab-num wide'); inp.type = 'number'; inp.min = 1; inp.max = 100000000; inp.value = 27; inp.setAttribute('aria-label', 'Starting number');
    row.appendChild(el('span', 'lab-lbl', 'Start at')); row.appendChild(inp); [27, 97, 871, 6171, 837799].forEach(function (r) { btn(row, String(r), function () { inp.value = r; draw(); }, 'mono'); });
    var code = el('div', 'codebox', '<pre>while n != 1 {\n  if n % 2 == 0 { n = n / 2 } else { n = 3 * n + 1 }\n}</pre>'), out = el('div'), sum = el('p', 'lab-sum'); fig.appendChild(row); fig.appendChild(code); fig.appendChild(out); fig.appendChild(sum);
    function draw() {
      var n = Math.max(1, Math.min(100000000, Math.floor(+inp.value) || 1)), seq = [n], peak = n;
      while (n !== 1 && seq.length < 2000) { n = n % 2 === 0 ? n / 2 : 3 * n + 1; seq.push(n); if (n > peak) peak = n; }
      var W = 600, H = 170, lp = Math.log(peak + 1), pts = seq.map(function (v, i) { return (10 + i * (W - 20) / Math.max(1, seq.length - 1)).toFixed(1) + ',' + (H - 12 - (Math.log(v + 1) / lp) * (H - 24)).toFixed(1); }).join(' ');
      out.innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="The values the loop passes through"><polyline points="' + pts + '" class="cz"/></svg>';
      sum.innerHTML = 'Starting from ' + seq[0].toLocaleString('en-US') + ' the loop runs <b>' + (seq.length - 1) + '</b> times and climbs to ' + peak.toLocaleString('en-US') + ' before it reaches 1 (height drawn on a logarithmic scale). Every number anyone has tried ends at 1. Nobody has proved that every number does.';
    }
    inp.addEventListener('input', draw); draw();
  };

  // ---------------------------------------------------------------- home: one program, every form it takes
  F.home = function (fig) {
    var wrap = el('div', 'homefig'), left = el('div', 'hf-l'), right = el('div', 'hf-r'); wrap.appendChild(left); wrap.appendChild(right); fig.appendChild(wrap);
    left.appendChild(el('div', 'hf-cap', 'A program. Edit it.'));
    var ed = editor(left, GCD), tabs = el('div', 'hf-tabs'), out = el('div', 'hf-out'); tabs.setAttribute('role', 'tablist'); right.appendChild(tabs); right.appendChild(out);
    var T = [['bytes', 'Bytes', '/program/text/'], ['tokens', 'Tokens', '/program/tokens/'], ['tree', 'Tree', '/program/tree/'], ['types', 'Types', '/program/types/'], ['ins', 'Instructions', '/stack/compilers/'], ['run', 'Run', '/program/execution/']], cur = 'run';
    T.forEach(function (t) { var b = btn(tabs, t[1], function () { cur = t[0]; draw(); }); b.dataset.t = t[0]; b.setAttribute('role', 'tab'); });
    function draw() {
      var src = ed.value, html = '', more = T.filter(function (t) { return t[0] === cur; })[0];
      tabs.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-selected', String(b.dataset.t === cur)); });
      try {
        if (cur === 'bytes') { var by = new TextEncoder().encode(src); html = '<p class="hf-note">What is actually stored: ' + by.length + ' numbers between 0 and 255.</p><pre class="hexdump">' + Array.prototype.slice.call(by, 0, 160).map(function (x) { return (x < 16 ? '0' : '') + x.toString(16); }).join(' ') + (by.length > 160 ? ' …' : '') + '</pre>'; }
        else if (cur === 'tokens') { var tk = tokensHtml(src); html = '<p class="hf-note">' + tk.n + ' tokens: the words and symbols of the language.</p><div class="toks">' + tk.html + '</div>'; }
        else if (cur === 'tree') { html = '<p class="hf-note">The structure the grammar finds. Indentation here means "is part of".</p><div class="olbox">' + outline(M.parse(src), 0) + '</div>'; }
        else if (cur === 'types') { html = '<p class="hf-note">What kind of value each name holds, worked out without running anything.</p>' + typesHtml(src); }
        else if (cur === 'ins') { var b = M.build(src), h2 = ''; Object.keys(b.code).forEach(function (k) { h2 += '<h4>' + esc(k) + '</h4><ol class="exins">' + b.code[k].code.map(function (x, i) { return '<li><i>' + i + '</i>' + esc(M.fmtIns(x)) + '</li>'; }).join('') + '</ol>'; }); html = '<p class="hf-note">The same program as instructions for a simple machine.</p>' + h2; }
        else { var bb = M.build(src), vm = new M.VM(bb.code).run(200000); html = '<p class="hf-note">The machine followed ' + vm.steps.toLocaleString('en-US') + ' instructions and printed:</p><pre class="exout big">' + esc(vm.out.join('\n') || '(nothing)') + (vm.error ? '\n' + esc(vm.error.msg) : '') + '</pre>'; }
      } catch (er) { html = errHtml(src, er); }
      out.innerHTML = html + '<p class="hf-more"><a href="' + more[2] + '">More about this form →</a></p>';
    }
    ed.addEventListener('input', draw); draw();
  };

  document.querySelectorAll('figure[data-fig]').forEach(function (fig) {
    var f = F[fig.dataset.fig]; if (!f || !M) return;
    var ns = fig.querySelector('.nojs'); if (ns) ns.remove();
    var cap = fig.querySelector('figcaption'), holder = el('div', 'lab'); fig.insertBefore(holder, cap);
    if (fig.dataset.a) holder.dataset.a = fig.dataset.a; if (fig.dataset.b) holder.dataset.b = fig.dataset.b;
    try { f(holder); } catch (er) { holder.innerHTML = '<p class="lab-err">This figure failed to start: ' + esc(er.message || er) + '</p>'; if (window.console) console.error(er); }
  });
})();
