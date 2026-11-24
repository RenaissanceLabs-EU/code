# Landmarks and open problems for the stack pages (research notes, 2026-11-25)

Output: data/landmarks-stack.json (9 sections). Entries have an optional extra field `more_urls` for second sources. Counts: physics 7/3, gates 6/3, machine 7/3, os 7/3, compilers 7/3, languages 6/4, apps 5/2, networks 7/3, learned 7/3 (landmarks/open).
Method: every entry was backed by a page fetched on 2026-11-25. Wikipedia was fetched only as a pointer for two items, marked below.

## Candidates that were wrong or imprecise, and what changed
- Transistor "1947 to 1948": the point-contact device was Dec 16 and Dec 23, 1947 (Bardeen, Brattain; Shockley present); the junction transistor was conceived in 1948. Entry uses 1947 and says so.
- Integrated circuit "Kilby 1958, Noyce 1959": correct, but they are different things. Kilby's Sept 12, 1958 circuit still used flying gold wires; Noyce's 1959 concept (patent filed July 1959, issued 1961) added metal over oxide. Merged into one entry, with Hoerni's planar process as its own entry (idea Dec 1957, disclosure Jan 1959, working transistor March 1959).
- MOSFET "1959 to 1960": the Computer History Museum dates the milestone 1960 but says the first successful device was 1959. Entry uses 1960 and states both.
- Dennard scaling "1974": correct for the IBM paper, but similar principles appeared in 1972 papers (Hoeneisen and Mead; Dennard's team). Stated in the text.
- Intel 4004 (1971) verified (CHM) but moved out; physics has no processor entry.
- EUV "in volume production": the best verifiable date is TSMC's N7+ (volume production Q2 2019, announced Oct 7, 2019). "First" is TSMC's own claim. ASML pages for shipment history were not reachable.
- Shannon "1937 thesis": the MIT record lists the thesis degree year as 1940; the AIEE paper is Transactions of the AIEE vol. 57 no. 12, 1938. Entry uses 1937 (writing) and states the other dates.
- NAND universality (Sheffer 1913): dropped. Could not fetch the paper; a bibliographic hit suggests Sheffer's original operation was "rejection" (NOR, not NAND), so the candidate is probably imprecise. Not verified.
- Mead and Conway "1980": the Computer History Museum's CAD page says 1979 and its catalog record says 1980. Entry uses 1979 and notes the catalog. The publisher is Addison-Wesley, not MIT Press.
- FPGA "Xilinx 1985": Freeman's patent priority date is March 12, 1984 and Xilinx was founded 1984; the XC2064 was introduced 1985 (Xilinx press release Nov 1, 1985 per IEEE). Entry uses 1985 and states both.
- Verilog and VHDL: only IEEE 1364-1995 (approved 1995-12-12) was verified. VHDL 1076-1987 could not be fetched.
- RISC "Berkeley RISC / Stanford MIPS around 1980": only the Patterson and Ditzel paper (SIGARCH CAN 8(6), October 1980) was verified; the Berkeley RISC and Stanford MIPS dates were not.
- x86 "1978": Intel's page confirms June 1978 for the 8086 (about 29,000 transistors).
- ARM "1985": the ARM1 chip was delivered to Acorn April 26, 1985 (Arm blog). The page does not say it worked on arrival.
- RISC-V "2010": started May 2010 at Berkeley's Par Lab; foundation formed 2015.
- WebAssembly "2017": the MVP design was declared complete by Chrome, Edge, Firefox and WebKit in Nov 2017; it became a W3C Recommendation Dec 5, 2019. Entry uses 2017 and states 2019.
- Unix "1969 to 1971, rewritten in C 1973": Ritchie's paper says Unix was born in 1969, the PDP-11 was proposed early 1970, pipes came in 1972 and the kernel was rewritten in C "during 1973" (not a specific season). Split into two entries.
- Multics: Bell Labs withdrew April 1969, so "Multics then Unix" ordering is loose; CTSS first demonstrated Nov 1961 (folded into the Multics entry). Used 1965 (Fall Joint Computer Conference papers).
- seL4 "2009": SOSP 2009 paper, ~8,700 lines of C and 600 of assembler. The seL4 site itself gives no proof date, so the paper is the source.
- Linux "1991": the announcement was Aug 25, 1991; version 0.01 date is uncertain (about mid-September 1991).
- POSIX "1988": IEEE 1003.1-1988 board approval Aug 22, publication Sept 30, 1988; it revised a 1986 trial-use version.
- Docker "2013": dropped. The GitHub release page shows v0.1.0 tagged 26 March but without the year, and the Docker blog page had nothing on history.
- A-0 "1952": the Computing History archive calls it her first compiler; other accounts call it closer to a linker-loader and credit Glennie's 1952 work as a rival first, so "first compiler" is debated (stated in the text).
- FORTRAN "1957": IBM's page says the system debuted in 1957 after funding in 1953; it does not give April 1957.
- Lisp "garbage collection (McCarthy 1960)": not confirmed from the fetched page, so the entry only says what the page states. Not verified.
- BNF and ALGOL 60: the fetched report text uses a "BNF-like" notation; its authors list includes Backus and Naur; revised report approved by IFIP TC 2 in Aug 1962.
- LR parsing (Knuth 1965): dropped, no fetchable primary copy.
- SSA: Brown tech report CS-91-21 is dated March 1991; the TOPLAS version is Oct 1991 and a preliminary version is POPL 1989 (those two from search listings only). Entry uses 1991.
- LLVM "2003": the CGO paper is March 2004. Entry uses 2004.
- Relational model: IBM's page dates System R to 1973, not 1974 to 1979, and says SQL was developed concurrently.
- Xerox Alto: sources disagree. The CHM blog says the project began 1972; Lampson says Alto system software began mid-1973. Entry uses 1972 and states both. The first machine's date was not verified.
- World Wide Web: proposal March 1989; first server and browser by end of 1990; the August 1991 announcement (the day "6 August" was not on the fetched page); source released royalty-free April 30, 1993 (the page does not say "public domain").
- SQLite: project page gives two different links for the start (2000-05-09 and 2000-05-29). Entry says May 2000.
- ACID (Haerder and Reuter 1983, Gray 1981): dropped, not verified.
- Ethernet "1973": ETHW does not give May 22, 1973 for the memo, so the exact date was not verified.
- TCP/IP "Cerf and Kahn 1974": RFC 675 (Dec 1974, Cerf, Dalal, Sunshine) was verified; the Cerf and Kahn IEEE paper was not fetched.
- DNS: RFC 882 (Nov 1983), later obsoleted by RFC 1034/1035.
- TLS 1.3: RFC 8446 (Aug 2018) is now marked superseded by RFC 9846.
- CAP, Raft, Paxos, Byzantine, MapReduce: verified but not used to keep entries at seven. Available if wanted: Byzantine Generals (TOPLAS 4(3), July 1982, Lamport page); Part-Time Parliament (submitted 1990, TOCS 16(2) May 1998); Raft (USENIX ATC 2014 best paper, raft.github.io); MapReduce (OSDI 2004, research.google). CAP was not fetched.
- Backpropagation "1986": Wikipedia (pointer only) gives Nature 323, 1986; Nature itself was blocked. Wikipedia also gives conflicting dates for earlier work, so none are used.
- Cybenko 1989 verified via mlanthology (MCSS 2, 303 to 314); AlphaGo (Oct 2015 Fan Hui 5-0, March 2016 Lee Sedol 4-1, DeepMind page) and AlphaCode (arXiv Feb 8, 2022, top 54.3 percent) and SWE-bench (arXiv Oct 10, 2023, 2,294 tasks, 1.96 percent best baseline) were verified but are not used. Copilot 2021 was not verified.

## Not verified (left out)
Sheffer 1913 NAND; VHDL 1076-1987; Docker 2013; Berkeley RISC and Stanford MIPS dates; Manchester Baby (June 21, 1948; the university page moved, CHM page had no entry); Codd paper text itself (the PDF was a scan; IBM's page used); Diffie-Hellman 1976 and RSA 1977 (PDFs were scans, Turing pages blocked; the venue IEEE Trans. Inf. Theory IT-22(6), Nov 1976 and CACM 21(2), Feb 1978 appear only in search listings); CAP theorem; Knuth LR; Simula, COBOL, ML, C 1972, SQL 1974, Java, JavaScript, npm, CPAN; Lisp garbage collection; Landauer's own 1961 paper; end-user programming open problem (Ko et al. 2011, PDF unreadable), so apps has only 2 open problems; the Mead and Conway "fall 1979" date (from search only).
Sources that blocked fetches (403): nobelprize.org, ACM Turing pages, IEEE Xplore, nature.com, ams.org, Springer, nokia.com Ritchie pages (the MIT-hosted copy of Ritchie's paper worked).
Wikipedia pointers used: Shannon thesis publication details; backpropagation paper details.
