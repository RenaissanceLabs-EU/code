// Mini: a very small programming language that runs in the page, so the figures on this site show real work, not pictures of it.
// One file, no dependencies: lexer, parser, type checker, constant folder, compiler to bytecode, and a stack machine.
// Grammar (statements end at a newline or ';'):
//   program := (fn | stmt)*
//   fn      := 'fn' name '(' params ')' block
//   stmt    := name '=' expr | 'if' expr block ('else' (block | if))? | 'while' expr block | 'return' expr? | expr
//   expr    := ||  &&  == != < <= > >=  + -  * / %  unary - !  call  literal  ( expr )
// Values are whole numbers and booleans. '#' starts a comment. print(x) writes a line.
(function (root) {
  'use strict';
  var KW = { fn: 1, 'while': 1, 'if': 1, 'else': 1, 'return': 1, 'true': 1, 'false': 1 };
  var OPS = ['==', '!=', '<=', '>=', '&&', '||', '+', '-', '*', '/', '%', '<', '>', '!', '='];
  function Err(msg, s, e) { this.msg = msg; this.s = s; this.e = e === undefined ? s + 1 : e; }

  // ---------------------------------------------------------------- lexer
  function lex(src) {
    var toks = [], i = 0, n = src.length, line = 1;
    while (i < n) {
      var c = src[i];
      if (c === '\n') { toks.push({ t: 'nl', v: '\n', s: i, e: i + 1, line: line }); i++; line++; continue; }
      if (c === ' ' || c === '\t' || c === '\r') { i++; continue; }
      if (c === '#') { var j = i; while (j < n && src[j] !== '\n') j++; toks.push({ t: 'comment', v: src.slice(i, j), s: i, e: j, line: line }); i = j; continue; }
      if (c >= '0' && c <= '9') { var k = i; while (k < n && src[k] >= '0' && src[k] <= '9') k++; toks.push({ t: 'num', v: src.slice(i, k), s: i, e: k, line: line }); i = k; continue; }
      if (/[A-Za-z_]/.test(c)) { var m = i; while (m < n && /[A-Za-z_0-9]/.test(src[m])) m++; var w = src.slice(i, m); toks.push({ t: KW[w] ? 'kw' : 'id', v: w, s: i, e: m, line: line }); i = m; continue; }
      if ('(){},;'.indexOf(c) >= 0) { toks.push({ t: c === ';' ? 'nl' : 'punct', v: c, s: i, e: i + 1, line: line }); i++; continue; }
      var op = null;
      for (var o = 0; o < OPS.length; o++) if (src.substr(i, OPS[o].length) === OPS[o]) { op = OPS[o]; break; }
      if (op) { toks.push({ t: 'op', v: op, s: i, e: i + op.length, line: line }); i += op.length; continue; }
      throw new Err('This character is not part of the language: ' + JSON.stringify(c), i);
    }
    toks.push({ t: 'eof', v: '', s: n, e: n, line: line });
    return toks;
  }

  // ---------------------------------------------------------------- parser
  var PREC = [['||'], ['&&'], ['==', '!='], ['<', '<=', '>', '>='], ['+', '-'], ['*', '/', '%']];
  function parse(src) {
    var toks = lex(src).filter(function (t) { return t.t !== 'comment'; }), p = 0;
    function peek() { return toks[p]; }
    function is(t, v) { var k = toks[p]; return k.t === t && (v === undefined || k.v === v); }
    function eat(t, v, what) { if (!is(t, v)) { var k = toks[p]; throw new Err('Expected ' + (what || v || t) + ' but found ' + (k.t === 'eof' ? 'the end of the program' : k.t === 'nl' ? 'the end of the line' : JSON.stringify(k.v)), k.s, k.e); } return toks[p++]; }
    function skipNl() { while (is('nl')) p++; }
    function block() {
      var open = eat('punct', '{'), body = []; skipNl();
      while (!is('punct', '}')) { if (is('eof')) throw new Err('This block is never closed with }', open.s, open.e); body.push(stmt()); endStmt(); }
      var close = eat('punct', '}');
      return { body: body, s: open.s, e: close.e };
    }
    function endStmt() { if (is('punct', '}') || is('eof')) return; eat('nl', undefined, 'a new line'); skipNl(); }
    function stmt() {
      var t = peek();
      if (is('kw', 'if')) return ifStmt();
      if (is('kw', 'while')) { p++; var c = expr(), b = block(); return { k: 'While', cond: c, body: b.body, s: t.s, e: b.e }; }
      if (is('kw', 'return')) { p++; var v = (is('nl') || is('punct', '}') || is('eof')) ? null : expr(); return { k: 'Return', value: v, s: t.s, e: v ? v.e : t.e }; }
      if (is('kw', 'fn')) throw new Err('Functions can only be defined at the top level', t.s, t.e);
      if (t.t === 'id' && toks[p + 1].t === 'op' && toks[p + 1].v === '=') { p += 2; var val = expr(); return { k: 'Assign', name: t.v, value: val, s: t.s, e: val.e, ns: t.s, ne: t.e }; }
      var x = expr(); return { k: 'ExprStmt', expr: x, s: x.s, e: x.e };
    }
    function ifStmt() {
      var t = eat('kw', 'if'), c = expr(), th = block(), el = null, end = th.e, save = p;
      skipNl();
      if (is('kw', 'else')) { p++; if (is('kw', 'if')) { var nested = ifStmt(); el = [nested]; end = nested.e; } else { var eb = block(); el = eb.body; end = eb.e; } }
      else p = save;
      return { k: 'If', cond: c, then: th.body, 'else': el, s: t.s, e: end };
    }
    function expr(level) {
      level = level || 0;
      if (level === PREC.length) return unary();
      var l = expr(level + 1);
      while (is('op') && PREC[level].indexOf(peek().v) >= 0) { var op = toks[p++].v, r = expr(level + 1); l = { k: 'Bin', op: op, l: l, r: r, s: l.s, e: r.e }; }
      return l;
    }
    function unary() {
      var t = peek();
      if (is('op', '-') || is('op', '!')) { p++; var x = unary(); return { k: 'Un', op: t.v, e1: x, s: t.s, e: x.e }; }
      return primary();
    }
    function primary() {
      var t = peek();
      if (t.t === 'num') { p++; return { k: 'Num', v: parseInt(t.v, 10), s: t.s, e: t.e }; }
      if (is('kw', 'true') || is('kw', 'false')) { p++; return { k: 'Bool', v: t.v === 'true', s: t.s, e: t.e }; }
      if (t.t === 'id') {
        p++;
        if (is('punct', '(')) {
          p++; var args = [];
          if (!is('punct', ')')) { args.push(expr()); while (is('punct', ',')) { p++; args.push(expr()); } }
          var cl = eat('punct', ')');
          return { k: 'Call', name: t.v, args: args, s: t.s, e: cl.e, ns: t.s, ne: t.e };
        }
        return { k: 'Var', name: t.v, s: t.s, e: t.e };
      }
      if (is('punct', '(')) { p++; var inner = expr(); var c2 = eat('punct', ')'); return { k: 'Paren', e1: inner, s: t.s, e: c2.e }; }
      throw new Err('Expected a value here but found ' + (t.t === 'eof' ? 'the end of the program' : t.t === 'nl' ? 'the end of the line' : JSON.stringify(t.v)), t.s, t.e);
    }
    var prog = { k: 'Program', fns: [], body: [], s: 0, e: src.length };
    skipNl();
    while (!is('eof')) {
      if (is('kw', 'fn')) {
        var f = toks[p++], name = eat('id', undefined, 'a function name'); eat('punct', '(');
        var params = [];
        if (!is('punct', ')')) { params.push(eat('id', undefined, 'a parameter name').v); while (is('punct', ',')) { p++; params.push(eat('id', undefined, 'a parameter name').v); } }
        eat('punct', ')'); var b = block();
        if (prog.fns.some(function (g) { return g.name === name.v; })) throw new Err('The function ' + name.v + ' is defined twice', name.s, name.e);
        prog.fns.push({ k: 'Fn', name: name.v, params: params, body: b.body, s: f.s, e: b.e, ns: name.s, ne: name.e });
      } else prog.body.push(stmt());
      endStmt();
    }
    return prog;
  }

  // ---------------------------------------------------------------- types (inference by unification: int, bool, nothing)
  function check(prog) {
    var next = 0;
    function tv() { return { tv: ++next, ref: null }; }
    function find(t) { while (t && t.tv && t.ref) t = t.ref; return t; }
    function show(t) { t = find(t); return t.tv ? '?' : t; }
    function unify(a, b, node, what) {
      a = find(a); b = find(b);
      if (a === b) return;
      if (a.tv) { a.ref = b; return; }
      if (b.tv) { b.ref = a; return; }
      throw new Err(what + ': expected ' + a + ' but this is ' + b, node.s, node.e);
    }
    var sigs = {};
    prog.fns.forEach(function (f) { sigs[f.name] = { params: f.params.map(tv), ret: tv(), fn: f }; });
    var scopes = {};
    function scopeOf(name, params, ptypes) { var sc = {}; params.forEach(function (p, i) { sc[p] = ptypes[i]; }); scopes[name] = sc; return sc; }
    function ex(n, sc) {
      switch (n.k) {
        case 'Num': return 'int';
        case 'Bool': return 'bool';
        case 'Paren': return ex(n.e1, sc);
        case 'Var': if (!sc[n.name]) throw new Err('The name ' + n.name + ' is used before it has a value', n.s, n.e); return sc[n.name];
        case 'Un': if (n.op === '-') { unify('int', ex(n.e1, sc), n.e1, 'Negation needs a number'); return 'int'; } unify('bool', ex(n.e1, sc), n.e1, '! needs a true or false value'); return 'bool';
        case 'Bin':
          var l = ex(n.l, sc), r = ex(n.r, sc);
          if ('+-*/%'.indexOf(n.op) >= 0) { unify('int', l, n.l, 'Arithmetic (' + n.op + ') needs numbers'); unify('int', r, n.r, 'Arithmetic (' + n.op + ') needs numbers'); return 'int'; }
          if (n.op === '&&' || n.op === '||') { unify('bool', l, n.l, n.op + ' needs true or false values'); unify('bool', r, n.r, n.op + ' needs true or false values'); return 'bool'; }
          if (n.op === '==' || n.op === '!=') { unify(l, r, n.r, 'Both sides of ' + n.op + ' must have the same type'); return 'bool'; }
          unify('int', l, n.l, 'Comparison (' + n.op + ') needs numbers'); unify('int', r, n.r, 'Comparison (' + n.op + ') needs numbers'); return 'bool';
        case 'Call':
          if (n.name === 'print') { if (n.args.length !== 1) throw new Err('print takes exactly one value', n.s, n.e); ex(n.args[0], sc); return 'nothing'; }
          var sg = sigs[n.name]; if (!sg) throw new Err('There is no function called ' + n.name, n.ns, n.ne);
          if (sg.params.length !== n.args.length) throw new Err(n.name + ' takes ' + sg.params.length + ' value' + (sg.params.length === 1 ? '' : 's') + ' but got ' + n.args.length, n.s, n.e);
          n.args.forEach(function (a, i) { unify(sg.params[i], ex(a, sc), a, 'Argument ' + (i + 1) + ' of ' + n.name); });
          return sg.ret;
      }
    }
    function st(n, sc, ret) {
      switch (n.k) {
        case 'Assign': var t = ex(n.value, sc); if (find(t) === 'nothing') throw new Err('This call gives back nothing, so there is nothing to store', n.value.s, n.value.e); if (!sc[n.name]) sc[n.name] = tv(); unify(sc[n.name], t, n.value, 'The variable ' + n.name + ' holds one type of value'); break;
        case 'If': unify('bool', ex(n.cond, sc), n.cond, 'The condition of if must be true or false'); n.then.forEach(function (s) { st(s, sc, ret); }); (n['else'] || []).forEach(function (s) { st(s, sc, ret); }); break;
        case 'While': unify('bool', ex(n.cond, sc), n.cond, 'The condition of while must be true or false'); n.body.forEach(function (s) { st(s, sc, ret); }); break;
        case 'Return': if (!ret) throw new Err('return only makes sense inside a function', n.s, n.e); unify(ret, n.value ? ex(n.value, sc) : 'nothing', n.value || n, 'This function returns one type of value'); break;
        case 'ExprStmt': ex(n.expr, sc); break;
      }
    }
    function returns(body) { return body.some(function (s) { return s.k === 'Return' || (s.k === 'If' && s['else'] && returns(s.then) && returns(s['else'])); }); }
    prog.fns.forEach(function (f) {
      var sg = sigs[f.name], sc = scopeOf(f.name, f.params, sg.params);
      f.body.forEach(function (s) { st(s, sc, sg.ret); });
      if (!returns(f.body)) unify(sg.ret, 'nothing', f, 'Not every path through ' + f.name + ' returns a value');
    });
    var top = scopeOf('(top level)', [], []);
    prog.body.forEach(function (s) { st(s, top, null); });
    var out = { fns: [], vars: [] };
    prog.fns.forEach(function (f) {
      var sg = sigs[f.name];
      out.fns.push({ name: f.name, params: f.params.map(function (p, i) { return { name: p, type: show(sg.params[i]) }; }), ret: show(sg.ret),
        locals: Object.keys(scopes[f.name]).filter(function (v) { return f.params.indexOf(v) < 0; }).map(function (v) { return { name: v, type: show(scopes[f.name][v]) }; }) });
    });
    Object.keys(top).forEach(function (v) { out.vars.push({ name: v, type: show(top[v]) }); });
    return out;
  }

  // ---------------------------------------------------------------- constant folding (the simplest compiler optimization)
  function fold(n) {
    if (!n || typeof n !== 'object') return n;
    if (Array.isArray(n)) return n.map(fold);
    var c = {}; for (var k in n) c[k] = (k === 's' || k === 'e' || k === 'ns' || k === 'ne') ? n[k] : fold(n[k]);
    if (c.k === 'Paren' && (c.e1.k === 'Num' || c.e1.k === 'Bool')) return c.e1;
    if (c.k === 'Un' && c.op === '-' && c.e1.k === 'Num') return { k: 'Num', v: -c.e1.v, s: c.s, e: c.e };
    if (c.k === 'Bin' && c.l.k === 'Num' && c.r.k === 'Num') {
      var a = c.l.v, b = c.r.v, v;
      switch (c.op) {
        case '+': v = a + b; break; case '-': v = a - b; break; case '*': v = a * b; break;
        case '/': if (b === 0) return c; v = Math.trunc(a / b); break; case '%': if (b === 0) return c; v = a % b; break;
        case '==': return { k: 'Bool', v: a === b, s: c.s, e: c.e }; case '!=': return { k: 'Bool', v: a !== b, s: c.s, e: c.e };
        case '<': return { k: 'Bool', v: a < b, s: c.s, e: c.e }; case '<=': return { k: 'Bool', v: a <= b, s: c.s, e: c.e };
        case '>': return { k: 'Bool', v: a > b, s: c.s, e: c.e }; case '>=': return { k: 'Bool', v: a >= b, s: c.s, e: c.e };
        default: return c;
      }
      if (!Number.isSafeInteger(v)) return c;
      return { k: 'Num', v: v, s: c.s, e: c.e };
    }
    return c;
  }

  // ---------------------------------------------------------------- compiler: tree -> instructions for a stack machine
  var BIN = { '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '%': 'MOD', '==': 'EQ', '!=': 'NE', '<': 'LT', '<=': 'LE', '>': 'GT', '>=': 'GE' };
  function compile(prog) {
    var code = {};
    function gen(body, isFn) {
      var out = [];
      function emit(op, a, n, b) { out.push({ op: op, a: a, b: b, s: n ? n.s : 0, e: n ? n.e : 0 }); return out.length - 1; }
      function ex(n) {
        switch (n.k) {
          case 'Num': emit('PUSH', n.v, n); break;
          case 'Bool': emit('PUSH', n.v, n); break;
          case 'Paren': ex(n.e1); break;
          case 'Var': emit('LOAD', n.name, n); break;
          case 'Un': ex(n.e1); emit(n.op === '-' ? 'NEG' : 'NOT', undefined, n); break;
          case 'Bin':
            if (n.op === '&&' || n.op === '||') {   // short circuit: the right side runs only when it can change the answer
              ex(n.l); if (n.op === '||') emit('NOT', undefined, n);
              var jz = emit('JZ', 0, n); ex(n.r); var jmp = emit('JMP', 0, n);
              out[jz].a = out.length; emit('PUSH', n.op === '||', n); out[jmp].a = out.length;
            } else { ex(n.l); ex(n.r); emit(BIN[n.op], undefined, n); }
            break;
          case 'Call': n.args.forEach(ex); if (n.name === 'print') emit('PRINT', undefined, n); else emit('CALL', n.name, n, n.args.length); break;
        }
      }
      function st(n) {
        switch (n.k) {
          case 'Assign': ex(n.value); emit('STORE', n.name, n); break;
          case 'ExprStmt': ex(n.expr); emit('POP', undefined, n); break;
          case 'Return': if (n.value) ex(n.value); else emit('PUSH', null, n); emit('RET', undefined, n); break;
          case 'If':
            ex(n.cond); var jz = emit('JZ', 0, n.cond); n.then.forEach(st);
            if (n['else']) { var j = emit('JMP', 0, n); out[jz].a = out.length; n['else'].forEach(st); out[j].a = out.length; } else out[jz].a = out.length;
            break;
          case 'While':
            var top = out.length; ex(n.cond); var jz2 = emit('JZ', 0, n.cond); n.body.forEach(st); emit('JMP', top, n); out[jz2].a = out.length; break;
        }
      }
      body.forEach(st);
      if (isFn) { emit('PUSH', null, null); emit('RET', undefined, null); } else emit('HALT', undefined, null);
      return out;
    }
    prog.fns.forEach(function (f) { code[f.name] = { params: f.params, code: gen(f.body, true) }; });
    code['(top level)'] = { params: [], code: gen(prog.body, false) };
    return code;
  }
  function fmtIns(i) { return i.op + (i.a === undefined ? '' : ' ' + (i.a === null ? 'nothing' : i.a)) + (i.b === undefined ? '' : ' ' + i.b); }

  // ---------------------------------------------------------------- the machine
  function VM(code, entry, args) {
    this.code = code; this.out = []; this.steps = 0; this.done = false; this.error = null; this.result = undefined;
    var f = code[entry || '(top level)'], locals = {};
    (args || []).forEach(function (v, i) { locals[f.params[i]] = v; });
    this.frames = [{ fn: entry || '(top level)', pc: 0, locals: locals, stack: [] }];
  }
  VM.prototype.frame = function () { return this.frames[this.frames.length - 1]; };
  VM.prototype.current = function () { var f = this.frame(); return f ? this.code[f.fn].code[f.pc] : null; };
  VM.prototype.step = function () {
    if (this.done) return false;
    var f = this.frame(), ins = this.code[f.fn].code[f.pc], S = f.stack, a, b, self = this;
    function fail(m) { self.error = new Err(m, ins.s, ins.e); self.done = true; return false; }
    function num(v) { return Number.isSafeInteger(v) ? v : null; }
    this.steps++; f.pc++;
    switch (ins.op) {
      case 'PUSH': S.push(ins.a); break;
      case 'LOAD': if (!(ins.a in f.locals)) return fail('The name ' + ins.a + ' has no value yet'); S.push(f.locals[ins.a]); break;
      case 'STORE': f.locals[ins.a] = S.pop(); break;
      case 'POP': S.pop(); break;
      case 'NEG': S.push(-S.pop()); break;
      case 'NOT': S.push(!S.pop()); break;
      case 'ADD': case 'SUB': case 'MUL': case 'DIV': case 'MOD':
        b = S.pop(); a = S.pop();
        if ((ins.op === 'DIV' || ins.op === 'MOD') && b === 0) return fail('Division by zero');
        a = ins.op === 'ADD' ? a + b : ins.op === 'SUB' ? a - b : ins.op === 'MUL' ? a * b : ins.op === 'DIV' ? Math.trunc(a / b) : a % b;
        if (num(a) === null) return fail('The number got too large for this machine');
        S.push(a); break;
      case 'EQ': b = S.pop(); a = S.pop(); S.push(a === b); break;
      case 'NE': b = S.pop(); a = S.pop(); S.push(a !== b); break;
      case 'LT': b = S.pop(); a = S.pop(); S.push(a < b); break;
      case 'LE': b = S.pop(); a = S.pop(); S.push(a <= b); break;
      case 'GT': b = S.pop(); a = S.pop(); S.push(a > b); break;
      case 'GE': b = S.pop(); a = S.pop(); S.push(a >= b); break;
      case 'JMP': f.pc = ins.a; break;
      case 'JZ': if (!S.pop()) f.pc = ins.a; break;
      case 'PRINT': a = S.pop(); this.out.push(String(a)); S.push(null); break;
      case 'CALL':
        if (this.frames.length >= 200) return fail('Too many nested calls (the call stack is full)');
        var g = this.code[ins.a], locals = {}, argv = S.splice(S.length - ins.b, ins.b);
        g.params.forEach(function (p, i) { locals[p] = argv[i]; });
        this.frames.push({ fn: ins.a, pc: 0, locals: locals, stack: [] }); break;
      case 'RET':
        a = S.pop(); this.frames.pop();
        if (!this.frames.length) { this.result = a; this.done = true; return false; }
        this.frame().stack.push(a); break;
      case 'HALT': this.done = true; f.pc--; return false;
    }
    return true;
  };
  VM.prototype.run = function (max) {
    max = max || 200000;
    while (!this.done) { if (this.steps >= max) { this.error = new Err('Stopped after ' + max + ' steps. The program may never finish.', 0, 0); this.error.timeout = true; this.done = true; break; } this.step(); }
    return this;
  };

  function build(src, opts) {
    var ast = parse(src); var types = check(ast);
    if (opts && opts.fold) ast = fold(ast);
    return { ast: ast, types: types, code: compile(ast) };
  }
  function run(src, max) { var b = build(src); var vm = new VM(b.code).run(max); return { out: vm.out, error: vm.error, steps: vm.steps }; }
  function callFn(built, name, args, max) {
    if (!built.code[name]) return { error: new Err('There is no function called ' + name, 0, 0) };
    if (built.code[name].params.length !== args.length) return { error: new Err(name + ' takes ' + built.code[name].params.length + ' values', 0, 0) };
    var vm = new VM(built.code, name, args).run(max || 20000); return { value: vm.result, error: vm.error, steps: vm.steps, out: vm.out };
  }
  var api = { lex: lex, parse: parse, check: check, fold: fold, compile: compile, VM: VM, build: build, run: run, callFn: callFn, fmtIns: fmtIns, Err: Err };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.Mini = api;
})(typeof window !== 'undefined' ? window : this);
