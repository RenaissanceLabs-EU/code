# Research notes: languages A (22 entries)

Output: `data/languages-a.json`. Checked 2026-11-24 (fetches ran late on the 24th into the 25th).
Languages: verilog, vhdl, assembly, wasm, c, cpp, rust, zig, go, ada, java, csharp, kotlin, swift, scala,
python, javascript, typescript, ruby, php, perl, lua.

## Method
- History facts (year, designers, influences, how it runs) were confirmed against pages fetched with curl in this
  pass; the URLs are in each entry's `sources`.
- "Written largely in X" claims: where the project's own site did not say it in plain words, the claim rests on the
  GitHub languages API (`repos/OWNER/REPO/languages`), fetched 2026-11-24. The percentage and date are in the
  `text`. These numbers move.
- Samples: the same Euclid gcd(48, 18) program. 10 of 22 were run here: assembly (AArch64, exit status 6), c, cpp,
  rust, swift, python, javascript, typescript (Deno and Bun), ruby, perl. Temp files only under `mktemp -d`.

## Things that changed and are worth knowing
- Bun is no longer a Zig showcase: `oven-sh/bun` is 77.9% Rust on 2026-11-24. It was left out of the Zig entry.
- `microsoft/TypeScript` is 84.6% Go on 2026-11-24 (the native port announced March 2025), so the TypeScript
  compiler is not listed as "written in TypeScript".
- Zig has no 1.0; latest release is 0.17.1 (2026-11-02) per ziglang.org/download/index.json.
- Wikipedia lists Java SE 27 (September 2026) as the latest Java release. Not used in the data.

## Judgment calls
- `family` for Swift is `managed` (automatic memory management, app language) although it compiles to native code
  and has no virtual machine; the `what` text says so. Move it to `systems` if that reads better on the site.
- `family` for Go is `systems`, with `level` `networks` (Kubernetes, Docker, Terraform).
- `family` for Scala is `managed` (JVM), not `functional`.
- `level` for C++ is `compilers` (V8, LLVM), for Perl `os` (system administration and text tools).
- C# year is 2000 (first widely distributed implementation, per the ECMA-334 introduction); 1.0 was January 2002.
- Scala year is 2003 (Odersky: "first released in 2003"); some sources say January 2004 for the first public
  version. Kotlin year is 2011 (unveiling), 1.0 was February 2016. WebAssembly year is 2017 (browser consensus).
- The Zig sample is 15 lines, over the 12-line target, because idiomatic Zig needs explicit mutable copies.
- The Scala sample is tail recursive (idiomatic); all others use a loop.
- The Ada sample prints " 6" with a leading space (behavior of 'Image).
- The assembly sample prints nothing and returns 6 as the exit status, to stay short.
- The WebAssembly sample exports gcd; a host must call it. WebAssembly itself cannot print.

## Not verified
- Sources that refused automated fetches (HTTP 403 or timeout), so the fact rests on Wikipedia as a pointer:
  - C: Ritchie's "The Development of the C Language" (bell-labs.com / nokia.com returned 403). Year 1972, designer
    and influences (B, BCPL, ALGOL 68) come from Wikipedia, which cites that paper.
  - C: the WG14 site (open-std.org) timed out, so `official_url` could not be checked today and `spec_url` is null.
  - Java: Oracle history pages returned 403. "May 1995" and "James Gosling" come from Wikipedia. The JLS and JVMS
    pages (fetched) confirm the relation to C and C++ and the bytecode model.
  - Ada: adaic.org returned 403. "1977 to 1983" and the influences (Pascal, ALGOL 68, Simula) come from Wikipedia.
    Jean Ichbiah as team lead and the Department of Defense contract are confirmed in the Ada Reference Manual.
  - Verilog: the ACM HOPL history paper was not fetched. 1984, the designers (Moorby, Goel, Huang) and the
    influences (C, Ada, Pascal) come from Wikipedia. Wikipedia also lists Fortran as an influence; left out.
  - VHDL: 1983 contract, Intermetrics/IBM/Texas Instruments and IEEE 1076-1987 come from Wikipedia. The Ada
    influence is confirmed in the GHDL documentation.
  - Assembly: the 1947 Booth and Britten report "Coding for A.R.C." is cited through Wikipedia, not read.
- Samples not run (no toolchain on this Mac, nothing installed): verilog, vhdl, zig, go, ada, java (launcher stub
  only, no runtime), csharp, kotlin, scala, php, lua. They are short and written with care, but untested.
- WebAssembly: the text-format sample was not assembled (no wat2wasm or wasm-tools). Only a hand-encoded binary
  with the same instruction sequence was run in Node.js (gcd(48,18)=6, gcd(17,5)=1, gcd(0,7)=7).
- The Verilog sample was not checked against a specific simulator; it uses Verilog-2001 ANSI function ports.
- TypeScript designer: Anders Hejlsberg is the author of the March 2025 Microsoft post on the compiler port; no
  fetched page states "designed by" in those words.
- Kotlin: no fetched page names a lead designer, so `designers` is just "JetBrains". Andrey Breslav wrote the 1.0
  announcement; Dmitry Jemerov wrote the 2011 unveiling post.
- Zig `influenced_by` is only `c` (the 2016 post frames Zig against C). No fetched page lists other influences.
- WebAssembly and assembly have empty `influenced_by`; no fetched source lists influences.
- Lua `influenced_by`: Modula, CLU, C++ and the in-house predecessor SOL are confirmed in lua.org/history.html.
  Scheme, SNOBOL and AWK are often cited but were not confirmed in the passage read, so they are left out.
- Perl `influenced_by` uses the id `bash` for "sh"; the Perl docs say "sed, awk, and sh". Bash itself is from 1989,
  after Perl, so the main session may prefer the plain name "sh".
- Go's first-release date in `year_note` (November 10, 2009) is from the Go FAQ; the Google Open Source blog post
  carries the same date.
- GRLIB (VHDL entry): the Gaisler page only says its open source models are VHDL. That LEON processors are built
  from GRLIB was not confirmed in text and is not claimed.
- Chromium was dropped as a C++ example because the GitHub API returned no language data for the mirror; V8's own
  docs ("written in C++") are used instead.
- Not checked and so not claimed: Minecraft (Java), Unity engine internals, Roblox/Luau usage, Instagram or
  Dropbox (Python), GitHub or Shopify (Ruby), NVIDIA's SPARK firmware, Boeing 777 (Ada), market-share figures.
- `used_for` phrases, `paradigms`, `typing` and a few explanatory clauses in `what` (for example "rarely written by
  hand" for WebAssembly) are standard descriptions and are not each tied to a fetched quote.
- Two JetBrains blog URLs return HTTP 202 to curl (content was served and read). All other URLs returned 200
  except open-std.org (timeout).
