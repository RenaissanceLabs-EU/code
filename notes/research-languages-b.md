# Research notes: data/languages-b.json (22 languages), 2026-11-24

Output: `data/languages-b.json`, a JSON list of 22 entries in this order:
r, julia, matlab, lisp, haskell, ocaml, erlang, elixir, fortran, cobol, sql, prolog, bash, powershell,
html-css, hcl, lean, rocq, isabelle, tlaplus, dafny, solidity.

## Method
- Every year, designer, influence and "runs" fact was checked against a page fetched in this pass (curl plus
  text search, or WebFetch where a site refused curl). The URL is in the entry's `sources` or in the notable's `url`.
- GitHub facts (creation dates, language shares) come from the GitHub REST API, fetched 2026-11-24.
- Moving numbers carry a date: CRAN 25835 packages and Bioconductor 3.23 with 2418 packages, both read 2026-11-24.

## Samples
Same program everywhere: Euclid's algorithm and gcd(48, 18) = 6.

Ran on this Mac (3 of 22), re-run from the final JSON text:
- sql: sqlite3 3.51.0, printed 6 (recursive common table expression).
- bash: GNU bash 3.2.57, printed 6.
- lean: Lean 4.36.0, no Mathlib; `#eval` printed 6 and the theorem `gcd_zero` was accepted with no warnings.

Not run (no toolchain installed; nothing was installed): r, julia, matlab, lisp, haskell, ocaml, erlang, elixir,
fortran, cobol, prolog, powershell, hcl, rocq, isabelle, tlaplus, dafny, solidity. html-css has nothing to run.

Notes on particular samples:
- julia, lisp, haskell, matlab, isabelle: the function is named `euclid` because the language already ships a `gcd`.
- cobol: 15 lines, over the 12 line limit; the four divisions are required for a full program. Prints 0006.
- tlaplus: 12 lines (limit was under 12). It is Figure 2 of Lamport, "Euclid Writes an Algorithm: A Fairytale"
  (https://lamport.azurewebsites.net/pubs/euclid.pdf), retyped in ASCII from the PDF, kept whole. It is the
  subtraction form of the algorithm, not the remainder form used in the other samples.
- rocq: definition copied in shape from Rocq's own `Corelib/Init/Nat.v` (`Fixpoint gcd`), fetched from the
  rocq-prover/rocq repository, with `Nat.modulo` written out instead of the `mod` notation. Note the argument
  order there: it recurses on the first argument.
- isabelle: definition only, no lemma, since it could not be checked.
- dafny: one lemma (`Gcd(a, 0) == a`) that needs a single unfolding; no assertion about `Gcd(48, 18)` because
  that depends on verifier fuel and could not be checked.
- hcl: cannot express the algorithm (no loops, no recursion); the block declares only the first remainder, 12.
- html-css: no computation; the page states the answer.
- solidity: no SPDX comment because samples carry no comments; solc warns about that.

## Not verified
- 19 of 22 samples were not executed (list above). They were written against official documentation, but only
  sql, bash and lean are proven to run. Highest risk: isabelle (automatic termination proof by `fun`), rocq
  (guard checker on a user-level copy of the library definition), dafny, cobol (fixed-format columns), matlab
  (local function in a script file).
- matlab: the year of Cleve Moler's first Fortran MATLAB. The MathWorks history article gives only "the 1970s
  and early 1980s", so `year` is 1984 (PC-MATLAB debut). The founding year and founders of MathWorks were not
  stated on the fetched page and are left out. How MATLAB executes code internally (any JIT) is not stated.
  The Simulink notable rests on one sentence of the MATLAB product page.
- r: the 1993 date comes from Ihaka's "R: Past and Future History" as hosted on CRAN
  (https://cran.r-project.org/doc/html/interface98-paper/paper_2.html); the copy on the Auckland site returned 403.
- elixir: `year` 2011 is the creation date of the public GitHub repository, not a release. The earliest release
  I could confirm is v0.5.0 (May 2012), which the blog calls the first release since the language was rewritten.
  Clojure as an influence was not confirmed and is left out.
- erlang: the 1998 open source release date was not confirmed from a fetched page, so no date is given for it.
  WhatsApp's use of Erlang was not checked and is left out. RabbitMQ "is an Erlang project" rests on the Elixir
  home page listing it among Erlang projects and on its README's "Supported Erlang versions".
- cobol: no primary document for the 1960 report was fetched; year, CODASYL and FLOW-MATIC come from IBM's
  COBOL topic page. The Smithsonian COBOL page returned 403. The ISO standard (ISO/IEC 1989) was not fetched,
  so `spec_url` is null. `official_url` points at GnuCOBOL, which is one implementation, because the language
  has no single home page. `family` is set to `managed` for lack of a better fit among the 12 ids; COBOL has
  no virtual machine or garbage collector, so the main session may want to refile it.
- sql: iso.org returned 403, so `official_url` and `spec_url` are null (the standard is ISO/IEC 9075). The 1974
  date rests on IBM Research's publication page and a bibliography page; Crossref's record for the DOI shows
  1976, which looks like a metadata error.
- prolog: the ISO standard number (ISO/IEC 13211-1) was not fetched; `spec_url` is null. The exact university
  name in Marseille is not given.
- bash: the exact day of the first beta (7 or 8 June 1989) was not confirmed; the entry cites the GNU's Bulletin
  of June 1989, which says Brian Fox "is beta-releasing BASH".
- powershell: that "Monad" was PowerShell's code name is not stated on any page I fetched; the link between
  Snover's Monad Manifesto (2002) and PowerShell is general knowledge here, not a fetched fact. `influenced_by`
  lists only the Unix shells named in the manifesto.
- html-css: no single first-publication date for HTML was confirmed. `year` 1990 follows the WHATWG history
  section ("first five years (1990-1995)") and the W3C timeline. The "HTML Tags" document I fetched is from a
  1992 snapshot of the CERN site.
- lean: `influenced_by` is empty; no fetched page names Lean's influences.
- dafny: `influenced_by` is empty for the same reason. `year` 2008 is the Microsoft Research project date; the
  reference paper is from 2010.
- isabelle: the three designers are taken from the author list of "From LCF to Isabelle/HOL" (arXiv 1907.02836)
  and the 1986 date from the journal reference of Paulson's paper (arXiv cs/9301104); the Isabelle site itself
  names only the two universities.
- solidity: named designers are left out. Gavin Wood (proposal, August 2014), Christian Reitwiessner and Alex
  Beregszaszi appear only on Wikipedia and secondary sites; soliditylang.org gives only the November 2014
  preview at Devcon0, which is what `year_note` uses.
- tlaplus: Amazon and Cosmos DB use is taken from Lamport's own industrial-use page, not from the companies.
- julia: the Celeste petascale result and other well-known Julia projects were not confirmed and are left out.
- fortran: only two notables; large climate models other than WRF were not checked.
- GitHub API rate limit was hit near the end; language shares for a few repositories (ethereum/solidity,
  JuliaLang/julia, ocaml/ocaml, dafny-lang/dafny, rocq-prover/rocq, erlang/otp) were not read and no claim
  depends on them.
