# Fact-check of the prose (2026-11-25)

Scope: data/program.txt, data/stack.txt, data/pages/intelligence.html, the home-page essay and DESCENT table in tools/build.py, and the fact sentences in site_figs.js. Sources were fetched on 2026-11-25 unless marked "from memory". Computed checks used python3 3.9.6, node 22, Apple clang 17 (arm64), Lean 4.36, sqlite3 and bash.

## Wrong

W1. program.txt, machine page, example: "On the left, the four bytes of each instruction as stored in memory." (the listing shows 340000e1, aa0103e8, ...)
Wrong: those are the 32-bit instruction words written most significant byte first. AArch64 instructions are stored little-endian, so the first instruction sits in memory as e1 00 00 34. I compiled the C with clang -arch arm64 -O1 and found the bytes e1000034 e80301aa in the object file. The same applies to DESCENT "stored as the number 0B000020" (the number is right, the encoding of add w0, w1, w0 checks out; memory holds 20 00 00 0B).
Source: https://developer.arm.com/documentation/ddi0487/latest (A64 instructions are always little-endian); reproduced locally.
Corrected: "On the left, the 32-bit word that encodes each instruction (stored in memory with its lowest byte first). On the right, the same thing in assembly:"

W2. program.txt, machine page, figcap: "A made-up processor with two registers and five instructions".
Wrong: the processor in site_figs.js (F.cpu) has six opcodes: CMP, SUB, BEQ, BLT, JMP, HALT (OPC table). The program uses eight instructions of those six kinds.
Source: site_figs.js, F.cpu, OPC table (read directly).
Corrected: "A made-up processor with two registers and six kinds of instruction, small enough to watch."

W3. program.txt, types page: "In Python, `True` counts as the number 1, so a `gcd(48, True)` written the same way runs and quietly returns 1."
Wrong: with the site's own Python sample (a, b = b, a % b; return a), gcd(48, True) returns True, not 1 (it prints True). Only gcd(True, 48) returns 1. I ran it on Python 3.9.6.
Source: https://docs.python.org/3/library/functions.html#bool (bool is a subclass of int); reproduced locally.
Corrected: "In Python, `True` counts as the number 1, so a `gcd(48, True)` written the same way runs and quietly returns `True`, which equals 1."

W4. build.py DESCENT, compilers row: "In Python's virtual machine ... BINARY_ADD" with no version.
Wrong for current Python: BINARY_ADD exists in 3.9 (I ran dis on 3.9.6 and it shows it) but was merged into BINARY_OP in Python 3.11 (from memory, not re-fetched; check https://docs.python.org/3/whatsnew/3.11.html). The compilers page correctly says "shown here for Python 3.9". The DESCENT row presents it as what Python does today.
Corrected: "BINARY_ADD (Python 3.10 and earlier)" or "BINARY_OP (Python 3.11 and later)".

W5. build.py DESCENT, physics row: "A few thousand transistors open and close."
Wrong or unsupported. The site's own adder figure says 288 transistors for an 8-bit adder built from NANDs, so a 32-bit adder alone is about 1,150. A real core uses far more for fetch, decode, register reads and write-back. "A few thousand" matches neither.
Source: arithmetic from stack.txt and site_figs.js (72 NAND gates x 4 transistors per 8 bits).
Corrected: "At least a thousand transistors open and close for the addition itself, and many thousands more to fetch, decode and store the result. The answer is a pattern of voltages."

W6. stack.txt, networks page, notice: "A one-byte message still costs 58 bytes of addressing."
Wrong in two ways. The 58 bytes (14 Ethernet header + 4 FCS + 20 IPv4 + 20 TCP) are headers and a trailer, and include sequence numbers, checksums and a length or type field, not only addresses. And Ethernet pads any frame below 64 bytes, so a one-byte message becomes a 64-byte frame (5 bytes of padding), and 20 more byte-times go to preamble and gap on the wire.
Source: https://en.wikipedia.org/wiki/Ethernet_frame (64-byte minimum, 46-byte minimum payload, 8-byte preamble, 12-byte gap); IEEE 802.3.
Corrected: "A one-byte message still costs 58 bytes of headers and trailer, and Ethernet pads such a small frame up to 64 bytes. A large file pays about 4%."

## Needs a qualifier

Q1. program.txt, text notice: "The letters, digits and symbols that programming languages are built from take one byte each, exactly as in ASCII."
True of most languages' core syntax. Not true for Lean (the page's own example uses → ∣ ∧ ⟨ ⟩, three bytes each), Python and Swift identifiers, Julia, APL, and any string or comment.
Corrected: "In most languages the keywords, digits and operators take one byte each, exactly as in ASCII. Strings, comments and a few languages (Lean uses → and ∧) reach for characters outside it."

Q2. program.txt, text notice: "An emoji takes four bytes."
Most do, but not all. ❤ is 3 bytes, a skin-tone thumbs up is 8, a family emoji is 18, a flag is 8 (checked in python3).
Corrected: "A typical emoji takes four bytes, and ones built from several parts take many more."

Q3. program.txt, text example: "UTF-8, the encoding nearly all source code uses today."
I found no authoritative figure for source code (W3Techs-style numbers are for web pages). Soften.
Corrected: "UTF-8, the encoding most source code uses today."

Q4. program.txt, text example: "These values were fixed by the ASCII standard in the 1960s and have not changed since."
True for a, space and % (and the others used). ASCII was first published as ASA X3.4-1963 and revised in 1967, when some codes changed (the up arrow and left arrow became ^ and _).
Source: https://en.wikipedia.org/wiki/ASCII
Corrected: "These values were fixed by the ASCII standard in the 1960s and have not changed since for these characters."

Q5. program.txt, text lede (models): "A language model meets code at this layer and no other." and "nobody hands it the tree or the types."
Contradicted by the page's own later text (execution traces, diffs, compiler and test feedback in agent loops). Models also train on commit diffs and tool output.
Corrected: "A language model meets code mostly at this layer." and "because it is rarely handed the tree or the types."

Q6. program.txt, tokens lede: "it is the first thing every compiler and interpreter does."
Scannerless parsers and some PEG parsers have no separate lexing stage.
Corrected: "it is the first thing most compilers and interpreters do."

Q7. program.txt, tree lede: "the form in which nearly every tool thinks about code."
Grep, diff, line counters, and many models work on text; many compilers move on to an intermediate representation.
Corrected: "the form in which compilers, formatters and many analysis tools think about code."

Q8. program.txt, tree lede: "A text that does not fit the rules has no tree, and the machine refuses it outright. It makes no attempt to guess what you meant." Also ideas, "Syntax error ... The program is rejected before anything runs."
Not universal. Bash runs earlier lines before it hits a later syntax error (I ran printf 'echo before\nif then\n' | script: it prints "before" first). JavaScript inserts semicolons automatically, HTML parsers accept anything, and tree-sitter and IDE parsers build a tree with error nodes from broken code.
Source: https://tree-sitter.github.io/tree-sitter/ (error recovery); reproduced bash.
Corrected: "In most languages, a text that does not fit the rules has no tree, and the compiler refuses it. It does not guess what you meant." and "In most languages the program is rejected before anything runs."

Q9. program.txt, tree models: "a grammar can constrain a model as it writes so that it cannot produce an ungrammatical program."
Holds only for the grammar given (usually syntax, not types), and output cut off by a length limit is an unfinished program.
Corrected: "a grammar can constrain a model as it writes so that every token it emits keeps the text a valid prefix of a program in that grammar."

Q10. program.txt, types lede: "You cannot add a number to `true`."
Language dependent. The page's own example shows Python and JavaScript allow it.
Corrected: "In a statically typed language you cannot add a number to `true`."

Q11. program.txt, types lede and ideas: "A type can be read as a claim, and a program of that type as evidence" and proof lede: "a proposition is a type and a proof of it is a program of that type, so checking a proof is type checking."
Exact only for total, terminating languages. In an ordinary language an infinite loop has any type, so the logic proves everything. Also applies to Lean and Rocq, not to Isabelle, which the same sentence lists and whose kernel is not type checking in this sense.
Source: https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence ("naive application of the correspondence leads to an inconsistent logic").
Corrected: "In a language where every program terminates, a proposition is a type and a proof of it is a program of that type. In Lean and Rocq, checking a proof is type checking."

Q12. program.txt, execution lede: "A machine takes the first instruction, carries it out, and moves to the next ... That is all a computer ever does."
This is the programmer's model. Real processors overlap, reorder and run many instructions at once, and there are many cores.
Corrected: "...That is the model every programmer works with, and the hardware makes it look true."

Q13. program.txt, execution models: "Every strong training signal for code comes from this layer."
Contradicted by the proof page (a proof checker is the strongest signal) and by types (compiler errors).
Corrected: "Most strong training signals for code come from this layer."

Q14. program.txt, lede of Turing and intelligence.html: "In 1936 Alan Turing proved that no procedure can decide, for every program and input, whether the program will eventually stop." and "The same 1936 paper showed ... This is the halting problem".
Turing's paper did not state the halting problem. It proved the printing (circle-free) problem and the Entscheidungsproblem undecidable. The name "halting problem" is Martin Davis's, from lectures in 1952 and print in 1958. The result is equivalent.
Source: https://en.wikipedia.org/wiki/Halting_problem (history section)
Corrected: "In 1936 Alan Turing proved a result that comes to the same thing: no procedure can decide, for every program and input, whether the program will eventually stop." and "This is the halting problem, named later, and it is impossible in principle..."

Q15. program.txt, tests lede: "Tests can show that a bug is present. They cannot show that none remain."
Exhaustive testing of a small finite input space does show it.
Corrected: "Tests can show that a bug is present. Except when every possible input can be tried, they cannot show that none remain."

Q16. program.txt, tests models: "several well-known benchmarks had to be reissued with many more tests per problem once this was measured."
They were extended by a different group, and the originals remain in use. HumanEval+ has about 80 times and MBPP+ about 35 times as many tests as HumanEval and MBPP (EvalPlus, Liu, Xia, Wang, Zhang, NeurIPS 2023). SWE-bench Verified is a human-filtered subset, not a version with more tests.
Source: https://github.com/evalplus/evalplus
Corrected: "several well-known benchmarks were extended by other researchers with many more tests per problem once this was measured: HumanEval+ and MBPP+ have about 80 and 35 times as many tests as the originals."

Q17. program.txt, proof lede: "Real systems have been verified this way, among them the seL4 operating system kernel and the CompCert C compiler."
seL4 was verified in Isabelle/HOL and CompCert in Coq (now Rocq). Neither is "this way" in the Curry-Howard sense for seL4. The proof assumes correct compiler, assembly, boot code and hardware. CompCert's proof covers the passes from the C abstract syntax tree to assembly, not parsing and type checking, nor the system assembler and linker. seL4 is a microkernel.
Sources: https://sel4.systems/Verification/ ; https://compcert.org/compcert-C.html ; https://cgi.cse.unsw.edu.au/~kleing/papers/sosp09.html
Corrected: "Real systems have been verified with proof assistants, among them the seL4 microkernel (in Isabelle/HOL) and the CompCert C compiler (in Coq, now Rocq), under stated assumptions about what lies outside the proof."

Q18. program.txt, proof ideas: "Hoare triple :: A claim of the form: if this holds before the code runs, that holds after."
Standard Hoare triples are partial correctness: the claim holds if the code finishes.
Source: https://en.wikipedia.org/wiki/Hoare_logic
Corrected: "...if this holds before the code runs and the code finishes, that holds after."

Q19. program.txt, proof models: "It cannot be satisfied by a program that only works on the examples" and "Trusted kernel ... Only it has to be right."
Fine for the first claim, but proof checkers are also gamed in practice through unfinished-proof placeholders (sorry), added axioms and weak statements; the surrounding assumptions (axioms, the compiler, hardware) must be right too.
Corrected: "Only it has to be right, apart from the axioms and the system it runs on."

Q20. program.txt, change lede: "Version control systems such as Git keep every version and every change ... recorded for good."
Git keeps every committed snapshot, not every edit, and history can be rewritten (rebase, squash, force push) or truncated (shallow clones).
Corrected: "Version control systems such as Git keep every committed version, and the history stays unless someone rewrites it."

Q21. program.txt, change models: "Every public commit is a before, an after and a stated reason."
Many commit messages say nothing useful.
Corrected: "Most public commits are a before and an after, and many carry a stated reason."

Q22. stack.txt, learned lede: "So for the first time there is important software with no source code in the usual sense."
Evolved designs and genetic programming come earlier, though not important software. Soften.
Corrected: "So there is now important software with no source code in the usual sense."

Q23. stack.txt, networks lede: "so any layer can be replaced without the others noticing."
Layers leak. TCP's checksum covers IP addresses, so IPv6 changed TCP and UDP; QUIC replaced TCP and needed HTTP/3.
Corrected: "so a layer can be replaced with little change to the others, though not none."

Q24. stack.txt, networks lede: "machines fail one at a time without warning".
Failures are partial and sometimes correlated (power, switch, bad deploy).
Corrected: "machines fail partway, sometimes many at once, without warning".

Q25. stack.txt, networks example: "Typing an address and pressing Enter sets off at least four conversations ... DNS, TCP, TLS, HTTP".
Not with HTTP/3, which runs over QUIC on UDP and has no TCP, or with a cached DNS answer, or plain HTTP without TLS.
Source: https://www.rfc-editor.org/rfc/rfc9114.html
Corrected: "Typing an address and pressing Enter usually sets off four conversations (with HTTP/3, the TCP and TLS steps are done together by QUIC)".

Q26. stack.txt, networks notice: "Past 1,460 bytes the data no longer fits in one packet" and "Routers along the way read only the IP layer."
1,460 = 1,500 MTU minus 20 + 20, with no TCP options (real traffic with timestamps is 1,448; IPv6, PPPoE, VPNs and jumbo frames differ). Routers forwarding by IP header still rewrite Ethernet headers, and NAT, firewalls and load balancers read ports.
Corrected: "On a standard 1,500-byte link, past 1,460 bytes..." and "Routers along the way forward using only the IP layer."

Q27. stack.txt, networks models: "have not yet been turned into training environments at scale."
A claim of absence I could not verify. Say "to our knowledge".

Q28. stack.txt, apps lede: "Most of the world's code lives at this level".
No source for a share. Soften to "much".
Also: "The relational model, proposed by Edgar Codd in 1970, ... lets questions be asked in a declarative language, SQL". Codd's 1970 paper (CACM 13(6)) proposed relations and a data sublanguage; SQL was developed at IBM a few years later and departs from the model (duplicates, NULL).
Corrected: "The relational model, proposed by Edgar Codd in 1970, treats data as tables. SQL, developed a few years later, lets questions be asked in a declarative language."
Also "Transactions guarantee ... a transfer between two bank accounts cannot lose money halfway": true inside one database; across banks it takes extra protocols.

Q29. stack.txt, languages lede: "All general-purpose languages can compute exactly the same things, a fact known as Turing completeness".
Ignoring finite memory and input/output. Corrected: "can compute the same functions, given enough memory".
Also: "SQL gives up generality to make one kind of question effortless." SQL with recursive queries is Turing complete (a cyclic tag system has been written in it), and the same page says Euclid is "a recursive query" in SQL.
Source: https://wiki.postgresql.org/wiki/Cyclic_Tag_System
Corrected: "SQL gives up convenience at general programming to make one kind of question effortless."

Q30. stack.txt, languages notice: "Compare C with Python: the types disappear and so does the compile step."
Python compiles to bytecode, as the compilers page says. Corrected: "the types disappear and so does the separate compile step."

Q31. stack.txt, languages models: "A handful of languages, led by Python, JavaScript and Java".
Ranking depends on the measure. GitHub's Octoverse 2025 puts TypeScript first by contributors (August 2025), then Python, JavaScript, Java.
Source: https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/
Corrected: "led by Python, JavaScript, TypeScript and Java".

Q32. stack.txt, compilers lede: "A compiler is itself a program, usually written in the language it compiles, and compiled by an earlier version of itself."
Many are (GCC, rustc, GHC, Go), many are not (Clang compiles C in C++; Swift's compiler is C++; CPython's compiler is C). From memory, not re-fetched. Corrected: "often written in the language it compiles". Also "A just-in-time compiler translates the parts of a program that turn out to be used most" describes tiered JITs; some (the .NET JIT) compile every method on first call.

Q33. stack.txt, compilers example: "That decision, made over and over, is most of the speed difference between the two languages."
Overstated. Dynamic dispatch is one factor alongside interpreter dispatch, boxed integers and reference counting.
Corrected: "That decision, made over and over, is one of the main reasons for the speed difference between the two languages."

Q34. stack.txt, os lede: "An operating system is the program that starts first and stays in charge." (also @short)
Boot firmware and the bootloader run before the kernel, and a hypervisor or firmware can outrank it.
Corrected: "An operating system is the program that takes charge once the machine has booted."

Q35. stack.txt, os lede: "so that one program cannot read another's memory even if it tries."
Spectre and Meltdown showed ways around it, and kernel bugs do too. Corrected: "so that one program cannot read another's memory by ordinary means."

Q36. stack.txt, os lede: "Containers and sandboxes are operating system features ... They are how code written by a model is run without trusting it."
Containers share the host kernel and are weak isolation alone; strong setups add virtual machines or user-space kernels (gVisor, Firecracker). Corrected: "They are one of the ways code written by a model is run without trusting it, often together with virtual machines."

Q37. stack.txt, os example: "exit(0)  ask the system to end this process".
On Linux, a normal program ends with the exit_group call, which ends all threads; the exit system call ends one thread. write(1, "hello\n", 6) is right.
Source: https://man7.org/linux/man-pages/man2/exit_group.2.html
Corrected: "exit_group(0)" with the same explanation, or note that exit(0) is the C library call.

Q38. stack.txt, os notice: "Real systems choose slices of a few milliseconds as a compromise."
Microsoft's documentation says a Windows time slice is approximately 20 milliseconds.
Source: https://learn.microsoft.com/en-us/windows/win32/procthread/multitasking
Corrected: "Real systems choose slices from a few milliseconds to a few tens of milliseconds as a compromise."

Q39. stack.txt, machine lede: "Instructions are kept in the same memory as data ... That is what makes one machine able to do any job".
Harvard-architecture microcontrollers (AVR, PIC) keep them apart, and universality comes from the instruction set; the stored program makes reprogramming easy.
Corrected: "In most computers instructions are kept in the same memory as data... That is what lets one machine change jobs by loading a new program."

Q40. stack.txt, machine example: "The whole loop is 24 bytes."
The listing is cbz plus five instructions (24 bytes), but the loop itself is five instructions (20 bytes). The listing also leaves out the final mov and ret that clang emits (9 instructions, 36 bytes in all, verified with clang -arch arm64 -O1).
Corrected: "The loop is five instructions, 20 bytes, plus the test before it."

Q41. stack.txt, gates lede: "Feed a gate's output back into its input and the circuit can hold a bit".
A single gate fed back on itself oscillates or sticks. Memory comes from two gates feeding each other (a latch).
Corrected: "Feed two gates' outputs back into each other's inputs and the circuit can hold a bit."

Q42. stack.txt, gates models: "a bug in a manufactured chip is recalled."
Usually worked around with microcode, firmware or software; recalls are rare (Pentium FDIV, 1994, is the famous one). Corrected: "a bug in a manufactured chip can be fixed only by a new design, or worked around."

Q43. stack.txt, gates models: "the public Verilog on code hosts is a small fraction of a percent of what exists for Python."
I could not find a per-language size to confirm the ratio. Keep out or replace with "much smaller".

Q44. stack.txt, physics notice: "No current flows from supply to ground once the output has settled. That is why this design, called CMOS, runs cool enough to pack billions together."
Almost none; modern transistors leak, and heat still limits how many can be switched at once.
Corrected: "Almost no current flows from supply to ground once the output has settled (only a small leak). That is why this design, called CMOS, can pack billions together."

Q45. stack.txt, physics lede: "A current processor holds tens of billions of them".
True for phone and laptop chips (M4: 28 billion, source below); large GPUs and multi-die parts have hundreds of billions. Corrected: "A current processor holds tens of billions of them, and the largest chips hundreds of billions".
Source: https://www.apple.com/newsroom/2024/05/apple-introduces-m4-chip/

Q46. stack.txt, physics models: "The size of the models that can be trained, and the cost of running them, are set by how many transistors fit on a chip and how much energy each one uses."
Also memory bandwidth, interconnect, packaging and algorithms. Corrected: "are limited by".
Also: "No dataset teaches a model anything at this level, and none is filed here." Datasets for transistor-level analog circuit design exist; from memory, not re-fetched. Corrected: "No dataset in our catalog sits at this level."

Q47. stack.txt, gates lede: "In 1937 Claude Shannon showed ... describes circuits of switches exactly."
Right date for the thesis (MIT, 1937); the paper appeared in 1938. Fine as written if "1937" refers to the thesis.
Source: https://en.wikipedia.org/wiki/Claude_Shannon
Corrected: "In his 1937 master's thesis Claude Shannon showed..."

Q48. build.py DESCENT, gates row: "32 full adders ... one column at a time, passing carries along."
That is a ripple-carry adder. Real processors use carry-lookahead or prefix adders, as the adder figure itself says. Corrected: "In the simplest design, 32 full adders..., and real processors use faster adders."

Q49. build.py home essay: "A recipe, a law and a proof are all exact writing, but each needs a person to carry it out or to judge it."
A formal proof is judged by a machine, as the essay's own third paragraph implies. Corrected: "...a proof (in the ordinary sense)".
Also "a proof can be read as a program, and a program can be proved": exact for constructive proofs; classical proofs need extra machinery (Griffin 1990). Corrected: "a constructive proof can be read as a program".
Also "Code is the first way we found to put reasoning outside a human head and have it keep working": the Jacquard loom (1804) and mechanical calculators did this earlier (from memory, not re-fetched). Corrected: "Code is the most general way we have found...".
Also "That demand for total precision is the whole difficulty of programming": overstated. Corrected: "a large part of the difficulty".
Also "at every level, a machine can check the answer": the site's own pages say UI code and infrastructure are hard to verify. Corrected: "at many levels, a machine can check the answer."

Q50. intelligence.html, Rule 110: "has been proved able to carry out any computation whatsoever" (and NOTE in site_figs.js).
Cook's proof (Complex Systems 15(1), 2004) shows universality on a suitably prepared infinite row with a periodic background, simulating a cyclic tag system; the figure uses a finite wrapped row.
Source: https://www.complex-systems.com/abstracts/v15_i01_a01/
Corrected: "has been proved able to carry out any computation, given a suitable starting row of unlimited length."

Q51. intelligence.html, Collatz: "Here is how close to the surface that impossibility lies. The loop below is three lines long."
Implies this loop's halting is shown undecidable. It is open. Conway (1972) proved a generalization undecidable; Kurtz and Simon (2007) proved the all-inputs version of a related family undecidable.
Source: https://en.wikipedia.org/wiki/Collatz_conjecture
Corrected: "Here is how close to the surface the difficulty lies. The loop below is three lines long. Its halting is an open problem, and slightly more general loops of this kind are provably undecidable."
Also "open since the 1930s": supported (proposed 1937); verified up to about 2.36 x 10^21.

Q52. intelligence.html: "This one theorem explains the shape of software engineering."
Rice's theorem covers undecidability only for general programs; many practical limits are cost, not impossibility (finite systems can be model checked exactly). Corrected: "This theorem is one reason for the shape of software engineering."

Q53. intelligence.html: "A network's weights ... cannot be reviewed, type-checked or proved in any ordinary sense."
Formal verification of specific properties of small networks exists (Reluplex, VNN-COMP). The hedge "ordinary" covers it, but add "in general".
Corrected: "...cannot in general be reviewed or proved correct, though specific properties of small networks can be verified."

Q54. intelligence.html: "That is the practical reason code is the best understood subject for training: the feedback is exact, it is automatic, and it does not depend on anyone's opinion."
Tests are incomplete and can be gamed (the site's tests page says so). Corrected: "the feedback is automatic and, when the checks are good, exact."

Q55. intelligence.html: "Turing's paper ... This is the universal machine, and it is why software exists at all."
Overstated. Corrected: "and it is the theoretical basis of software."

Q56. site_figs.js NOTE, Rule 90 and Rule 250: Rule 90 is cell = left XOR right (verified) and gives the Sierpinski triangle from a single cell, but the figure wraps at 181 cells and runs 110 rows, so the triangle is distorted from row 91 (checked). Rule 250 is left OR right and draws an alternating pattern, not "just spreads"; "most rules are this dull" has no source.
Corrected: "Rule 90 draws the Sierpinski triangle from a single cell" and drop or source "Most rules are this dull".

## Confirmed

- a = b % 2 is nine characters, bytes 61 20 3D 20 62 20 25 20 32, é is C3 A9, tab is 09 (python3).
- UTF-8 uses one to four bytes per character (python3 spot checks, 1 to 4).
- Python bool arithmetic: True is 1 (python3). JavaScript "5" * 2 is 10, "5" + 2 is "52" (node).
- A full adder from nine NAND gates (exhaustive truth-table simulation, python3); 8 x 9 = 72 gates; 72 x 4 = 288 transistors.
- A CMOS NAND takes four transistors, two series NMOS and two parallel PMOS, output 0 only when both inputs 1 (circuit reasoning; consistent with the figure).
- Binary addition 100 + 58 = 158 as shown (python3).
- gcd on (48, 18): (18, 12), (12, 6), (6, 0), answer 6; thirteen instructions per trip (site compiler output, instructions 0 to 12).
- Euclid's gcd: 999,999 subtractions for (1,000,000, 1) versus one remainder step, and the subtractive version never finishes at zero (site VM).
- Test fig claims: "Off by one" passes 4 of 5; memorized version passes 5 of 5 and 0 of 5 held out (site VM).
- Changing b != 0 to a != 0 ends in division by zero (site VM).
- XOR network has 17 parameters (8 + 4 + 4 + 1); the training code reaches 4 of 4 within 100 steps for XOR, AND, OR, NAND from several seeds (node).
- ARM64 has no integer remainder instruction, udiv then msub; the listed instruction sequence and the words 340000e1 aa0103e8 1ac10809 1b018121 aa0803e0 35ffff81 match clang arm64 -O1/-O2 output; add w0, w1, w0 is 0B000020 (clang, otool).
- Python 3.9 bytecode for a + b is LOAD_FAST, LOAD_FAST, BINARY_ADD, RETURN_VALUE (python 3.9.6, dis).
- Lean code in program.txt compiles with no errors on Lean 4.36 (lean).
- SQL example runs and returns the rows in the stated order (sqlite3).
- 58 bytes = 14 + 4 + 20 + 20; 1,460 = 1,500 - 40; 58/1,518 = 3.8%, "about 4%" (arithmetic; Ethernet header 14, FCS 4, max payload 1,500 from the Wikipedia Ethernet frame page).
- 6/pi^2 = 0.6079, 60.8% (python3).
- Rule 110 universality by Matthew Cook, Complex Systems 15(1), 2004 (complex-systems.com abstract).
- Rule 30 center column used as a random number generator in Mathematica (Wikipedia, Rule 30; "previously used").
- Rule 90 is left XOR right; Rule 184 moves a car right when the next cell is free (truth-table check, python3).
- Moore 1965: components per integrated circuit doubling every year (Wikipedia, Moore's law, quoting the paper).
- Shannon thesis 1937 (Wikipedia, Claude Shannon).
- Codd, "A Relational Model of Data for Large Shared Data Banks", CACM 13(6), June 1970 (search result listing).
- Rice, Trans. AMS 74, 1953, pp. 358-366 (search result listing).
- Turing 1936 and Church 1936 dates; Collatz proposed 1937 (Wikipedia, Collatz conjecture); "ninety years" from 1936 is right for 2026.
- Apple M4 has 28 billion transistors (apple.com newsroom); "tens of billions" holds.
- seL4 described as a microkernel with machine-checked proofs (sel4.systems); CompCert verified in Coq, nearly all of C99 (compcert.org).
- Euclid's Elements around 300 BC and Euclid's algorithm as one of the oldest still in use: standard date, not re-fetched.
- Unix and C: no sentence in the checked files claims this, so nothing to confirm.
- Stored claim "Moore" and "6/" strings in site_figs.js: "Moore" does not appear in site_figs.js (only in stack.txt); "6/" appears once (6/pi^2, correct).
