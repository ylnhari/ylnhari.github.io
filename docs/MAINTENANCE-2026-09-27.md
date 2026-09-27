# Maintenance review — 2026-09-27

The initial pass covered maintenance tooling only. A subsequent authorized portfolio update adds Cross-Agent Bridge to the homepage, with the matching profile card maintained in the canonical resume source.

Cross-Agent Bridge is described as pre-release local messaging for live Claude Code and Codex sessions, with durable per-recipient delivery, retry handling, and explicit progress and reply states. Its repository remains the authority for capabilities and limitations. The card does not claim production readiness, remote authentication, or exactly-once processing.

`python scripts/check_links.py` passed for all 79 HTML pages before publication. Both new project links resolve to the same public repository and use the existing safe external-link relation. Career facts, existing resume variants, and assets are unchanged. Final deployed-page acceptance is recorded in the release evidence after synchronization.
