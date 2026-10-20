# ma-lit-bills

A neutral tracker of Massachusetts bills that touch technology, and of the law already on the books that they'd change. For each bill: where it stands, its committee and history, its sponsors, topic tags, and a short plain-language summary written or checked by a person. A weekly digest feeds the LITSA newsletter, and the tracker will appear at suffolklitsa.org/bills.

**Status:** data pipeline working against the Legislature's public API. Topic matching, review workflow and digest are in place. Summaries, hearings and the site page are next. Goal: fully running for the 2027-2028 session, when most bills are filed in January.

## Neutral by design

The tracker describes bills. It never supports or opposes one, never ranks them as good or bad, and never predicts whether they'll pass. LITSA members who want to testify or advocate do so as individuals, not through this project. The rules for summaries are in [docs/SUMMARIES.md](docs/SUMMARIES.md).

## Topics

AI · privacy and data protection · cybersecurity and breach notice · biometrics and facial recognition · government surveillance technology · kids' online safety · digital right to repair · broadband and telecommunications · autonomous vehicles · crypto and fintech · courts and legal technology · online platforms and e-commerce.

Each topic and the phrases that flag a bill for it are in [topics/topics.toml](topics/topics.toml). Current law: the General Laws sections in force on each topic, with their text, so a reader can see what a bill would change (issues #14 to #16). Later: court decisions interpreting these laws.

## How it works

```
malegislature.gov/api  (public, no key)
        │  scripts/fetch.py: every title in the session, one request
        ▼
topics/topics.toml  ── title matching ──►  candidates
        │
data/<court>/review.toml  ── a person confirms or rejects each candidate
        │
        ▼
data/<court>/bills.json   (details and history for every kept bill)
        │
        ├─► scripts/digest.py  ─► weekly newsletter section
        └─► suffolklitsa.org/bills (planned)
```

- **Title matching only finds candidates.** A person reads each one and confirms or rejects it in `review.toml`. Only confirmed bills appear in the digest or get summaries.
- The client waits a second between requests, identifies itself, and caches responses in `.cache/` so reruns are cheap.
- `<court>` is the General Court number: 194 is 2025-2026, 195 is 2027-2028.

## Run it

In a Codespace or with Python 3.11+ (nothing to install):

```
python3 scripts/fetch.py --court 194          # refresh bills.json (about five minutes; two requests per kept bill)
python3 scripts/validate.py                   # check the data
python3 scripts/digest.py --court 194 --since 2026-10-13
python3 -m unittest discover -s tests
```

## Layout

| Path | What's there |
|---|---|
| `topics/topics.toml` | Topic definitions and matching phrases |
| `data/<court>/bills.json` | Tracked bills. Generated; don't hand-edit (summaries are the exception, see below) |
| `data/<court>/review.toml` | Human decisions: confirmed and rejected bills, topic overrides |
| `lit_bills/` | API client, topic matcher, record builder |
| `scripts/` | `fetch.py`, `validate.py`, `digest.py` |
| `docs/` | Data contract, summary rules, roadmap, decisions |

## Contributing

There's work for coders and non-coders. Reviewing candidates and writing summaries need no code at all. Start with an issue labeled [`no code needed`](https://github.com/suffolklitsa/ma-lit-bills/labels/no%20code%20needed) or [`good first issue`](https://github.com/suffolklitsa/ma-lit-bills/labels/good%20first%20issue), and read [CONTRIBUTING.md](CONTRIBUTING.md).

Questions go in the Build topic on the LITSA GroupMe, or comment on the issue.

## Who owns what

- **Build:** the pipeline, the digest, the site page. Maintainer: Sam Darkwa (@drkwjr).
- **Research & Writing:** candidate review, topic definitions and every summary. Summaries don't merge until a second R&W member has checked them against the bill text.

## License

Code is MIT ([LICENSE](LICENSE)). Bill data comes from the Massachusetts Legislature's public API. Summaries are CC BY 4.0, credited to LITSA.
