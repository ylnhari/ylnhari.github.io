# Personal public website instructions

This is a public static portfolio and resume site. A push to `main` deploys it to GitHub Pages.

- Treat every content change as public publication.
- Preserve approved resume claims, employment history, credentials, endorsements, personal contact details, and linked assets unless the user explicitly asks to change them.
- Do not add private documents, credentials, tokens, local paths, analytics secrets, or unapproved personal data.
- Verify internal links, asset paths, responsive layout, and public-facing metadata after site changes.
- Do not commit, push, or trigger publication unless explicitly requested.

## Gates

- `python scripts/check_links.py` — fails if any internal href/asset path doesn't resolve to a real file; also warns (non-fatal) about tracked files no page links to.

## Living artifacts

**Re-check weekly; refresh on drift.**

This whole site is written in the present tense, so unlike a dated post it gets
*wrong* by sitting still. Re-check these against their sources:

| Claim | What goes stale | Source of truth |
|---|---|---|
| Current role, employer, and years of experience | Tenure phrasing ("10+ years", "Present") recomputes with time; role and employer change | The site owner — ask. Never retype a career fact from memory, from another page of this site, or from a third-party profile |
| Availability / "open to roles" line | Stops being true without anyone editing it | The site owner, explicitly |
| Project cards and their status badges | "IN PROGRESS", "Shipping in 2026", and the roster itself — shipped work goes missing, finished work still reads as pending | Each linked project's own repository |
| Figures quoted from other projects (model counts, GPU lists) | These are hand-typed copies of numbers those projects regenerate; the copy here drifts silently | That project's generated data file — not its README, which may itself be a stale copy of the same number |

Rules:
- A number that appears both here and in a linked project must be refreshed in
  the same pass in both places, or in neither. Two different values in public is
  worse than one old one.
- Career facts are frozen unless the site owner says otherwise — **flag** drift,
  do not correct it. Everything else on this list is a straightforward refresh.
- Verify links and layout after editing, and publish only on explicit request.
