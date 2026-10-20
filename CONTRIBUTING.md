# Contributing to ma-lit-bills

The org-wide guide is at [suffolklitsa/.github](https://github.com/suffolklitsa/.github/blob/main/CONTRIBUTING.md). This page covers what's specific here.

## Reviewing candidates (no code)

`scripts/fetch.py` flags bills whose titles match a topic phrase. Many are false hits. For each candidate:

1. Open its `url` and read the bill's text (or at least its first section).
2. If it's about technology in one of our topics, add it under `[confirmed]` in `data/<court>/review.toml`, with the right topics:
   ```toml
   [confirmed.H1234]
   topics = ["ai", "privacy"]
   reviewed_by = "Your Name"
   ```
3. If it isn't, add it under `[rejected]` with a short reason:
   ```toml
   [rejected.H5678]
   reason = "About tax privacy for farm records, not data privacy"
   reviewed_by = "Your Name"
   ```
4. Open a pull request. The next fetch applies your decisions.

Do a batch (10 to 25 bills) per pull request.

## Writing a summary (no code)

Only confirmed bills get summaries. Follow [docs/SUMMARIES.md](docs/SUMMARIES.md). Add the summary to the bill's `summary` field in `data/<court>/bills.json` (the one field you may hand-edit; fetch keeps it), with your name in `written_by`. A second R&W member checks it against the bill text and fills `reviewed_by` and `reviewed_on`.

## Code

- No dependencies beyond the Python standard library.
- Be polite to the API: keep the one-second spacing and the cache. Don't run full fetches in a loop.
- Changes to the data shape update `docs/DATA.md`, `scripts/validate.py` and the tests together.
- Run `python3 -m unittest discover -s tests` and `python3 scripts/validate.py` before opening a pull request.
