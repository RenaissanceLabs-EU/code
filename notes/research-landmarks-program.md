# Research notes: landmarks and open problems for the program layers (2026-11-25)

Output: data/landmarks-program.json (10 sections, 60 landmarks, 30 open problems). Bibliographic facts (title, authors, venue, year)
were checked against Crossref/OpenAlex records by DOI; descriptive claims against fetched abstracts, standards, project pages or the
paper text (stated per item below when the source was a secondary pointer).

## Candidates that were wrong or imprecise, and what changed

### text
- ASCII 1963: right (ASA X3.4-1963, major revision USAS X3.4-1967). The only source fetched is Wikipedia (pointer only; its text
  names Bob Bemer's May 1961 proposal and the X3.2 subcommittee). No primary standard text was found online.
- Unicode 1991: imprecise. Unicode 1.0 was printed in two volumes, Volume 1 in October 1991 and Volume 2 in June 1992 (unicode.org).
- UTF-8 "Thompson and Pike 1992, Plan 9": right, but refined. RFC 3629: devised September 1992 by Ken Thompson "following design
  criteria from Rob Pike". Pike's own history page: designed on a diner placemat in September 1992, Thompson's email of
  September 8, 1992 reworked the X/Open FSS-UTF proposal, and the "IBM designed it, Plan 9 implemented it" story traces to RFC 2279.
  Added RFC 3629 (November 2003, STD 63) as its own landmark.
- Literate programming 1984: right (The Computer Journal 27(2), 97-111). Knuth's own page does not give the 1984 date; the
  journal page does.
- Open "Trojan Source, 2021": the arXiv posting is 2021-10-30; the USENIX Security paper is 2023 (the project page says 2023).
  CVE-2021-42574 (reordering) and CVE-2021-42694 (homoglyphs).
- Open "line ending and encoding mismatches": no research paper found; used Git's own documentation instead.
- Added the identifier normalization problem (UAX #31) as the third open item.

### tokens
- lex 1975: right. Two dated documents exist: Lesk, CSTR 39, October 1975, and Lesk and Schmidt, July 21, 1975 (Unix 7th Edition
  manual). Source is Wikipedia as pointer (primary link dinosaur.compilertools.net did not load).
- BPE (Gage 1994): right (The C Users Journal, 1994, "A New Algorithm for Data Compression"); the primary text was unreachable
  (pennelynn.com refused connection), so the source is Wikipedia as pointer.
- Sennrich et al. 2016: arXiv v1 is August 31, 2015; the ACL 2016 venue gives the year 2016. Both stated.
- SentencePiece 2018: right (arXiv 2018-08-19, EMNLP 2018 demo).
- "Tokenization for code" as an open problem: not supported by a source I could fetch. Replaced by three sourced problems:
  number tokenization (Singh and Strouse 2024), under-trained tokens (Land and Bartolo 2024), tokenizer-free scaling (BLT 2024).
- Added ByT5 (2021) as a landmark.

### tree
- BNF "Backus, Naur": refined. Backus presented the notation at the June 1959 ICIP conference (cited in the ALGOL 60 report text
  itself); the 1960 ALGOL 60 report edited by Naur used it. The name "Backus normal form" came with the 1963 revised report and
  Knuth's 1964 letter proposed Backus-Naur form (both via Wikipedia, not used in the JSON).
- Chomsky hierarchy 1956: imprecise. The 1956 paper first described the general idea of a hierarchy of grammars; the modern
  hierarchy with context-free grammars is credited to Chomsky and Schutzenberger 1963 (via Wikipedia).
- yacc 1975: right; developed in the early 1970s, in Version 3 Unix, full description 1975 (Wikipedia pointer; the report link
  dinosaur.compilertools.net/yacc was not fetched).
- tree-sitter "2018": wrong as a start date. The GitHub repository was created 2013-11-06 and the earliest commits (December 2013)
  are by Max Brunsfeld (GitHub API). 2017 and 2018 are the years of talks listed in its docs. Year set to 2013.
- LSP 2016: this is the date of the June 27, 2016 standardization announcement (SD Times), not the first internal use in VS Code,
  for which no date was found. Origin story: Erich Gamma, after integrating OmniSharp and TypeScript.
- Open "grammar-constrained decoding" and "error-tolerant parsing": sourced to arXiv papers (Geng et al. 2023, Diekmann and Tratt
  2018, XGrammar 2024). The third open item is a related cost problem, since I found no separate sourced third topic.

### types
- Russell 1908: refined. The 1908 paper presents type theory as a foundation; the theory was first introduced in the 1903
  Principles of Mathematics (SEP).
- Church 1940: right (JSL 5, June 1940).
- Hindley 1969 and Milner 1978: right (TAMS 146; JCSS 17, December 1978). Milner independently developed an equivalent method.
- Curry-Howard: right but needs the two dates: Curry 1934 (PNAS 20), Howard manuscript 1969, published 1980 in the Seldin and
  Hindley volume (pp. 479-490). Note the correspondence is sometimes called Curry-Howard-de Bruijn.
- Martin-Löf "1970s": precise version: first published type theory is the 1973 presentation (Logic Colloquium '73) published in
  1975; 1971 and 1972 preprints exist; 1971 version was inconsistent (Girard). Source is Wikipedia as pointer for the history.
- Rust ownership types: the Rust 1.0 announcement (May 15, 2015) does not mention ownership or borrowing at all. The ownership
  rules are in the Rust Book; the formal result is RustBelt (POPL 2018). Year set to 2018, with 2015 in the text.
- Open items: gradual typing paper is Takikawa et al. POPL 2016; I only used its abstract.

### execution
- Turing 1936: the SEP says "1936-7" and Crossref dates the volume 1937. Stated as volume dated 1936-37.
- Imprecise candidate: the halting problem. Turing's 1936 paper does not prove the halting problem as such. His base problems
  are CIRC? and PRINT?; the familiar halting-problem proof is a later popular construction (SEP, Turing machine entry).
  The JSON therefore says "whether a machine will ever print a given symbol is uncomputable".
- Lambda calculus 1936: Church's two 1936 papers are "An Unsolvable Problem of Elementary Number Theory" (AJM 58) and
  "A Note on the Entscheidungsproblem" (JSL 1); the SEP lambda calculus entry does not give a 1936 introduction date and the
  early Church formulations were inconsistent. The entry is therefore framed as the unsolvability result, not the invention.
- McCarthy 1960 garbage collection: the paper describes the reclamation process; the word "garbage collection" appears only in a
  footnote added to the LaTeX copy ("We already called this process 'garbage collection', but I guess I chickened out of using
  it in the paper"). Text states exactly that.
- Plotkin 1981: right (DAIMI FN-19, Aarhus, 1981; JLAP 2004 reprint). Scott and Strachey 1971: the report on the Oxford PRG site
  carries a library stamp "4 OCT 1971".
- Added Landin 1964.
- Open "semantics for real languages": JavaScript has a mechanized spec (JSCert, POPL 2014) so it is not left as an open item;
  C pointer provenance and concurrent memory models are sourced instead.

### tests
- Harvard Mark II moth: the date September 9, 1947 and the caption "First actual case of bug being found" are confirmed
  (Computer History Museum). Imprecise candidate: the moth did not originate "bug". The term was already used (Edison letter 1878,
  Pall Mall Gazette 1889, Webster's 1934), "debug" appears in a 1945 aeronautical journal, the Smithsonian says the logbook was
  probably not Hopper's, and sources do not name who wrote the entry. Hopper helped make the story famous in lectures (CHM) but
  I found no source that she coined "bug" or "debugging".
- Dijkstra remark: exact words from "The Humble Programmer" (EWD 340, Turing Lecture 1972): "program testing can be a very
  effective way to show the presence of bugs, but is hopelessly inadequate for showing their absence." The common paraphrase
  "never their absence" is a different wording; an earlier version (EWD 249, 1970, and the 1969 NATO conference) was not reachable.
- SUnit and JUnit "late 1990s": JUnit was created in 1997 according to Fowler (flight to OOPSLA in Atlanta). SUnit's date is
  unresolved: a search result gives Beck's "Simple Smalltalk Testing: With Patterns" as 1989, another source as 1999; I did not
  verify either, so no SUnit year is stated.
- Fuzzing "Miller 1990, AFL": Miller et al. CACM December 1990 confirmed. AFL: first public release 0.21b on 2013-11-12
  (project ChangeLog), not a later year. The author name Michal Zalewski comes from general knowledge of the lcamtuf site.
- Mutation testing "1970s": the 1978 DeMillo, Lipton, Sayward paper states the coupling effect (abstract). I did not verify any
  earlier mutation-testing source (Lipton 1971, Hamlet 1977), so those are not claimed.
- QuickCheck 2000: right (ICFP 2000).
- Test-driven development (Beck): not included, see Not verified.

### proof
- Floyd 1967 and Hoare 1969: right (Proc. Symp. Applied Math. 19, 1967; CACM October 1969). Only Hoare's abstract was fetched.
- Dijkstra "weakest preconditions (1975)": the 1975 CACM paper is "Guarded commands, nondeterminacy and formal derivation of
  programs"; its abstract names the guarded commands and a calculus for derivation. The term "weakest precondition" is not in
  the abstract, so the JSON does not use it.
- LCF 1972: Milner's memo is Stanford AIM-169, May 1972 (DTIC AD0785072; the abstract was seen only through a search
  summary because the scan did not extract).
- Coq "1989": wrong. rocq-prover.org says the project began in 1984 as an implementation of the Calculus of Constructions at
  INRIA-Rocquencourt (Coquand and Huet) and in 1991 Paulin extended it to the Calculus of Inductive Constructions; I found no
  1989 source. The calculus paper is Coquand and Huet, Information and Computation 76, 1988. Coq is now the Rocq Prover. Not a
  separate landmark; Coq appears in the Gonthier, CompCert entries.
- Four color theorem "Coq 2005": Gonthier's report says it was fully checked by Coq v7.3.1; Microsoft Research says Gonthier and
  Werner completed the formal proof in 2005. The JSON gives 2005 and credits Gonthier with Werner. The Notices article (2008)
  could not be fetched; the report on cl.cam.ac.uk was read.
- CompCert "2006 to 2009": two papers. 2006 POPL: Cminor to PowerPC; 2009 CACM: Clight (large subset of C) to PowerPC.
- seL4 2009: right; the abstract's claim is quoted as "to our knowledge, the first formal proof of functional correctness of a
  complete, general-purpose operating-system kernel".
- Lean "de Moura 2013": the Lean history on lean-lang.org lists the first commit in July 2013; the "About" page credits de Moura.
  Mathlib3 created July 2017, Mathlib4 repository May 2021, port completed July 2023, Lean 4.0 September 2023.

### change
- SCCS 1975 (Rochkind, IEEE TSE, December 1975): right.
- diff 1976: right as Bell Labs CSTR 41; the scanned report is dated July 1976 while Wikipedia and a Usenet post say June 1976,
  stated in `text`. The link was not fetched directly (the Dartmouth host redirected to an outage page); the content comes from a
  search result excerpt of the scan. Hunt and Szymanski's CACM paper (May 1977) is the published companion.
- RCS: Tichy 1985 (SPE 15(7)). Note: the DOI I first used (10.1002/spe.4380150702) is a different paper (Contla); correct DOI
  is 10.1002/spe.4380150703.
- Git 2005: first commit 2005-04-07 by Linus Torvalds (git/git history, GitHub API).
- Continuous integration: Fowler's page says Beck developed CI as part of XP in the 1990s; some credit Booch with coining the
  term but, per Fowler, only in an offhand sentence. Fowler's article is dated September 10, 2000 (rewritten 2006 and 2024).
  The "Booch 1991" date was not verified, so it is not used.
- Not used: CVS, GitHub (2008) and semantic versioning (see Not verified).
- Open "supply chain security": xz backdoor (Freund, oss-security, March 29, 2024; CVE-2024-3094 per the mailing-list post).

### computation
- Hilbert 1928: the Entscheidungsproblem called "the main problem of mathematical logic" in Hilbert and Ackermann's 1928 book,
  p. 77 (SEP); a 1938 edition dropped the expectation after the Church-Turing result. Folded into the Church and Turing entry.
- Gödel 1931: SEP says the paper was published in January 1931 (announced September 7, 1930 at Königsberg); Crossref lists the
  journal volume as December 1931. Year 1931.
- Rice 1953: the theorem was proved in Rice's 1951 dissertation; the published paper is 1953 (TAMS 74(2), 358-366).
- Kolmogorov complexity "1960s": Solomonoff 1960 (preliminary report) and 1964 (Information and Control, 7); Kolmogorov 1965
  (Problems of Information Transmission); Chaitin submitted October 1966 (JACM). The entry is placed at 1964 (Solomonoff).
  Source is Wikipedia as pointer.
- Cook 1971 and Karp 1972: right; Levin (1973 publication) independently. 
- Rule 110: Cook, Complex Systems 15(1), 2004, confirming Wolfram's 1985 conjecture.
- BB(5): right and formalized. The proof was announced July 2, 2024 (bbchallenge.org) and is checked in Coq (arXiv 2509.12337, which
  appeared September 15, 2025): 181,385,789 five-state machines. The year in the JSON is 2024 (announcement); the paper is 2025.
- Open BB(6): the bbchallenge front page highlights a halting machine by mxdys (2025) showing BB(6) > 2↑↑↑5. A second page
  gave the bound 2↑↑(2↑↑(2↑↑10)), which is smaller and probably older; I used only the front page and dated the statement.
- P versus NP: the Clay page credits Cook and Levin, 1971.
- Collatz: Tao 2019 (arXiv 1909.03562).

### intelligence
- Turing 1950: Mind, October 1950; the volume is 59 (LIX), not 50 as the SEP page text says.
- Dartmouth: dated August 31, 1955, authors McCarthy, Minsky, Rochester, Shannon.
- Solomonoff 1964: moved to computation (algorithmic information), since it is about prediction and complexity.
- Program synthesis: Gulwani, POPL 2011 (the paper later known as Flash Fill, a name I did not verify).
- AlphaDev: Nature 618, June 7, 2023; abstract says the algorithms were integrated into the LLVM standard C++ library. The exact
  libc++ merge date was not verified.
- Models proving theorems in Lean: AlphaProof, Nature 651, published 2025-11-12, with AlphaGeometry 2 reached a silver-medal
  equivalent at IMO 2024. Other systems seen but not used as claims: Aristotle (arXiv 2510.01346, gold-medal-equivalent on
  IMO 2025 per its abstract), DeepSeek-Prover-V2 (arXiv 2504.21801).
- Nanda et al.: ICLR 2023 in the usual citation (arXiv January 2023); the grokking phenomenon is from Power et al. (arXiv
  January 2022).
- Added Codex (arXiv July 2021). Also seen but not used: Pearce et al., "Asleep at the Keyboard?" (arXiv August 2021) on the
  security of Copilot's suggestions.

## Not verified
- ASCII from a primary standards text (only Wikipedia was reachable). 
- UTF-8 and ASCII entries also rest on one source each; no second source was cross-checked.
- Gage 1994 text itself; lex and yacc reports themselves (only Wikipedia pointers and bibliographic data).
- Whether LSP existed inside VS Code before 2016, and its first release date.
- Coq 1989 first release (contradicted by 1984 start); Coq version history.
- SUnit year (1989 versus 1999); Beck and Gamma "Test Infected" (Java Report, July 1998), seen only in a search summary.
- Test-driven development: Beck's book (2002) was not confirmed (publisher page blocked).
- Dijkstra's earlier statements of the testing remark (1969 NATO conference, EWD 249).
- Mutation testing before 1978 (Lipton 1971, Hamlet 1977).
- GitHub launch date (Wikipedia timeline says April 10, 2008; github.blog did not confirm), semantic versioning's first publication
  date (semver.org gives no date; author Tom Preston-Werner), CVS, Booch's 1991 use of continuous integration.
- Hindley 1969 and Milner 1978 contents beyond title, Hindley abstract and Wikipedia's history.
- Scott and Strachey 1971 as the "founding" report for denotational semantics: only the report's title, author and date were
  checked. The JSON wording is a standard characterization I could not confirm from a fetched source; recheck before publishing.
- The Smithsonian record for the moth (si.edu blocked); the Smithsonian statements come through JSTOR Daily and a search summary.
- The exact LLVM libc++ merge date for AlphaDev routines.
- Turing's 1936 publication date to the month (the paper was read in November 1936 per general knowledge, not fetched).
- Fowler's description of 1997 JUnit creation was relayed by the fetch summarizer; re-read the page before quoting.
