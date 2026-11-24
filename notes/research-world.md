# Research notes: data/world.json ("Code in the world")

Pass run 2026-11-24 and 2026-11-25. Output: `data/world.json` with 17 systems, 10 failures, 9 living entries,
72 distinct source URLs. Every fact in the file was read from the linked page (or its text) during this pass.

## How things were checked

- Pages were fetched with WebFetch or curl and the relevant sentences read. PDFs (NASA MCO report, CrowdStrike
  root cause analysis, CSRB Log4j report, Senate Y2K report, the USENIX npm paper, the Google code review paper,
  the ECMWF article, the Visa fact sheet) were converted with pdftotext and searched for the exact passages.
- Live counters were read from the services' own endpoints on 2026-11-24: kernel.org releases.json,
  Software Heritage `/api/1/stat/counters/`, crates.io `/api/v1/summary`, `replicate.npmjs.com`, the pypi.org
  front page, the huggingface.co/models listing (`numTotalItems`).
- TOP500: the November 2026 operating system family figure (Linux 500 of 500) comes from the List Statistics form
  at https://www.top500.org/statistics/list/ (POST with list = November 2026, type = Operating system Family).
  The URL alone shows the form, not the number.

## URL status

All URLs return HTTP 200 to a scripted request except these, which block scripts (HTTP 403) but open normally:

- https://www.gao.gov/products/gao-16-468 and https://www.gao.gov/products/gao-19-471 (read through WebFetch and in a browser)
- https://www.iso.org/standard/68383.html (read in a browser)
- https://www.swift.com/about-us/who-we-are (read in a browser)
- https://www.sec.gov/news/press-release/2013-222 (read through WebFetch)

No paywalls. LWN's 7.3 statistics article was fully readable without a subscription on the day it was checked.

## Source caveats worth knowing

- Ariane 5: the `url` is ESA's official PDF of the inquiry report, which is a scan with no text layer. The wording
  was verified against ESA's press release N° 33-1996 (which quotes the report's conclusion) and against a text
  transcription of the report hosted at the University of Minnesota (listed in `sources`).
- Therac-25: the source is the Leveson and Turner paper (IEEE Computer, July 1993) as reprinted with permission
  on an MIT course site. It is the standard investigation, not a government report.
- Knight Capital: facts are from the SEC press release of 2013-10-16. The full administrative order
  (Release No. 34-70694, https://www.sec.gov/litigation/admin/2013/34-70694.pdf) returned 403 and was not read.
- Heartbleed: the OpenSSL advisory is at openssl-library.org (the project's current site); details on duration and
  discoverers are from heartbleed.com, run by the Codenomicon team that co-discovered it.
- Y2K: the 100 billion dollar figure is the Senate committee quoting a Commerce Department estimate. The Commerce
  report itself (commerce.gov) returned 403 and was not read.
- Swift's page gives both "more than 200" and "220+" countries and territories; the file uses neither.
- ISO 26262: only the catalog page for Part 1 was read. IEC 62304, IEC 61131-3 (newer edition) and DO-178C are
  paid documents and were not read; statements about them come from FDA, IEC and FAA catalog or regulatory pages.
- The Octoverse page says it was updated on 2026-02-28; the figures are for September 2024 through August 2025.
- `languages` on a few entries rest on common knowledge and not on a sentence in a fetched page: OpenSSL and
  SQLite (C), Heartbleed (C), xz (C, shell), Android kernel (C), AI tooling (Python). The caveat fields say so
  where it applies.

## Not verified

Popular claims that were looked for and could not be confirmed from a primary source in this pass. None of them
appears in the data file.

Size and line counts
- "The Linux kernel has N million lines of code." LWN's per-release article gives lines added and removed, not a
  total, and kernel.org states no total. Left out.
- "A modern car contains 100 million lines of code." No primary source found (AUTOSAR and ISO pages say nothing
  of the kind). Left out.
- "There are 200 (or 220, or 800) billion lines of COBOL in use." No primary source. IBM's COBOL product page
  makes no such claim. Left out.
- Size of a browser engine (Chromium, Gecko, WebKit) in lines of code. No figure on chromium.org. Left out.
- Lines of code in any airliner, in the F-35, or in the Apollo guidance software. Not sourced.

Shares and counts
- "COBOL handles 95 percent of ATM transactions" and "43 percent of banking systems run on COBOL". No primary
  source found.
- "N of the world's top 50 banks run on IBM Z" and "mainframes handle most of the world's card transactions".
  The current IBM Z product page carries no such statistic (only customer case studies). Left out.
- VisaNet's capacity in transactions per second (often quoted as 24,000 or 65,000). Not on Visa's current fact
  sheet. Left out.
- Number of active Android devices. No primary figure fetched.
- Android's or Linux's share of phones, servers or cloud workloads. Not sourced.
- Browser market shares. Not sourced.
- OpenSSL's current share of TLS servers. Only a 2014 Netcraft figure for Apache plus nginx was found (used, with
  caveat).
- "96 percent (or 97, or 70 to 90) of codebases contain open source." Comes from commercial audit reports that
  were not fetched. Left out.
- Share of code now written by AI, or number of AI model users. No solid source. Left out.

Costs
- Ariane 5 loss of 370 or 500 million dollars, and the loss of the four Cluster satellites as payload. The cost is
  not in the passages read; the Cluster payload was not confirmed in the text searched. Left out.
- Mars Climate Orbiter cost of 125 million (or 327.6 million for the program). Not in the mishap board report.
- Worldwide Y2K cost of 300 to 600 billion dollars. The Senate report cites several conflicting estimates and
  says the worldwide cost may never be known. Only the United States estimate is used.
- CrowdStrike outage cost of 5.4 billion dollars to Fortune 500 companies. From an insurer's estimate, not fetched.
- Heartbleed: "17 percent of secure web servers (about half a million) were vulnerable". From Netcraft, not fetched.
- Therac-25: exact number of deaths (usually given as three or more). The paper pages read say "deaths and
  serious injuries" without a count in the passages checked. Also "the software was written by one programmer in
  PDP-11 assembly language": it is in the paper's sidebars, which the reprint pages read did not include.
- Knight Capital details from the SEC order: the name "Power Peg", "7 of 8 servers", "154 stocks". The order PDF
  could not be fetched; only press release facts are used.
- left-pad being "11 lines of code" and npm restoring the original package. Not in the passages read.
- xz: CVSS score 10.0, the attacker persona's name and the multi-year timeline. The NVD page did not load; only
  Andres Freund's original report is used.
- Log4Shell: number of affected devices or exploitation attempts. The CSRB report itself says no authoritative
  source exists for exploitation trends.

Maintenance and process
- "60 to 80 percent (or 90 percent) of software cost is maintenance." The usual citations (Lientz and Swanson 1980,
  later textbooks) are not online as primary sources and could not be read. Left out. The file gives the GAO
  federal IT operations and maintenance share instead and says plainly that it is a different quantity.
- "The oldest code still running." No source establishes which code that is. The file gives documented ages only.
- Date of Git's first commit (April 2005) and "Git was written in about ten days". The Pro Git book gives only
  the year 2005.
- Reproducible Builds: share of Debian (or any distribution) packages that build reproducibly. Not fetched.
- Typical size of a dependency tree outside npm (PyPI, Maven, crates.io). Only the 2019 npm study was read, and
  its data ends in April 2018.

Not researched in this pass (candidates from the task that were skipped)
- LIGO and Event Horizon Telescope software.
- Mars rover flight software (Curiosity, Perseverance) beyond the Ingenuity helicopter, and the language of the
  James Webb flight software core (only its JavaScript onboard scripts are sourced).
- Fly-by-wire in specific aircraft.
- Power grid specifics (the file covers IEC 61131-3 only).
- DNS root server operations and BGP routing table size.
