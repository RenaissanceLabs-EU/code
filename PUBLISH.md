# Publishing plan (nothing below has been done)

Waiting for an explicit go-ahead before any of this.

1. Create the public repo `RenaissanceLabs-EU/code` (name is your call; `lean-arena` and `practice` set the pattern).
2. Initialize git in this folder, commit (`.gitignore` already excludes `tools/node/node_modules`), push to `main`.
3. GitHub Pages: Settings > Pages > Source: Deploy from a branch, `main`, folder `/docs`. `docs/CNAME` already contains `code.renaissancelabs.eu`. Enable "Enforce HTTPS" once the certificate is issued (can take up to an hour).
4. DNS in Spaceship, zone `renaissancelabs.eu`: add one record
   - Type `CNAME`, Host `code`, Value `renaissancelabs-eu.github.io` (same target that `math` and `practice` use today; verified with `dig`).
5. After DNS resolves: check https://code.renaissancelabs.eu, the social previews (e.g. paste the URL into a link-preview debugger), and run `node tools/page_check.mjs` against the live site if desired.
6. Optional follow-ups: link from renaissancelabs.eu and from the Math and Practice site footers (those repos are not touched by this work).
