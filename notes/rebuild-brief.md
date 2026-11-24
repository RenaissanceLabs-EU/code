# Rebuild brief (shared by all research passes), 2026-11-24

The site code.renaissancelabs.eu is being rebuilt to start from "what is code?" and to map the whole of programming,
the way math.renaissancelabs.eu maps mathematics. Research passes write JSON data files; the main session writes
the generator, the prose pages and the figures. Do not edit tools/build.py, docs/, site_*.js or other passes' files.

## Rules for every pass
- American English. No em dashes or en dashes used as punctuation (use commas, periods, parentheses). Plain, exact prose.
- Never invent. Every fact (year, name, number, "X is written in Y") must be confirmed NOW from a primary or
  authoritative source you actually fetched (official site, spec, the paper, the project's own repo or docs,
  Hugging Face API/card, GitHub API). Wikipedia is acceptable only as a pointer to find the primary source, or
  for uncontroversial dates when the primary source is not online; say so in the source note.
- Put the source URL next to the fact (fields named `url` / `sources`). If you cannot verify something, leave it
  out and list it in your notes file under "Not verified".
- Prefer fewer, solid entries to many shaky ones. Numbers that move (line counts, market shares) need a date.
- Write valid UTF-8 JSON. Validate with `python3 -c "import json;json.load(open(PATH))"` before finishing.
- Do not run anything heavy. No model downloads. Keep memory use small.
- Your final report: file paths written, counts, and the list of things you could not verify. Keep it short.

## Shared vocabulary

Stack level ids (bottom to top):
- `physics`   Transistors and physics: switches made from matter
- `gates`     Logic gates and digital design (hardware description languages live here)
- `machine`   Instruction sets and machine code (assembly, binaries, WebAssembly)
- `os`        Operating systems: kernels, processes, files, system calls, shells
- `compilers` Compilers and runtimes: translation, virtual machines, garbage collection
- `languages` Languages and libraries: what programmers actually write, package ecosystems
- `apps`      Applications and data: programs people use, databases, the web
- `networks`  Networks and distributed systems: protocols, the internet, consensus, infrastructure as code
- `learned`   Learned programs: neural network weights, programs found by training rather than written

Program layer ids (the forms one program takes):
`text`, `tokens`, `tree`, `types`, `execution`, `tests`, `proof`, `change`

Language family ids:
`hardware`, `machine`, `systems`, `managed`, `scripting`, `functional`, `numeric`, `query-logic`, `shell`,
`markup-config`, `proof`, `contract`

Language ids (44):
verilog, vhdl, assembly, wasm, c, cpp, rust, zig, go, ada, java, csharp, kotlin, swift, scala, python,
javascript, typescript, ruby, php, perl, lua, r, julia, matlab, lisp, haskell, ocaml, erlang, elixir, fortran,
cobol, sql, prolog, bash, powershell, html-css, hcl, lean, rocq, isabelle, tlaplus, dafny, solidity

## Existing catalog
- Merged catalog: docs/data/resources.json (319 entries). Source files: data/resources/*.json.
- Entry schema: see any entry in data/resources/evals.json. Required: id, name, kind
  (dataset|benchmark|environment|tool|model|recipe|paper), url, license (or null), size (or null), summary,
  stages (subset of pretrain,sft,preference,rl,eval,tooling), languages (list), tasks (subset of the ids in
  data/taxonomy.json), difficulty, how_to_use, caveats, released, checked ("2026-11-24"), evidence.
