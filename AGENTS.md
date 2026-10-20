# AGENTS.md

Instructions for AI coding agents working in this repo, and for the people using them. Read README.md and CONTRIBUTING.md too.

## What this repo is

A neutral tracker of Massachusetts tech bills, and of current law, built on the Legislature's public API (malegislature.gov/api). Standard-library Python.

## Commands

```
python3 -m unittest discover -s tests
python3 scripts/validate.py
python3 scripts/fetch.py --court 194      # live API; a few minutes; don't run in a loop
python3 scripts/digest.py --court 194 --since YYYY-MM-DD
```

## Rules for this repo

- **Branches:** work from `staging` and open pull requests against it. Never target `main`; maintainers promote `staging` to `main`.
- **Neutral, always.** Code, summaries and digest text describe bills. Never support, oppose, rank or predict. No adjectives that tell the reader how to feel.
- **Summaries come from bill text.** An agent may draft one, but a person checks it against the bill and a second R&W member reviews it. Never fill `reviewed_by` for someone.
- **Be polite to the API:** keep the one-second spacing and the cache, and don't add parallel requests. Tests use saved sample responses, never the live API.
- **`bills.json` is generated.** The only hand-edited field is `summary`. Review decisions go in `data/<court>/review.toml`.
- **Changing the data shape** means updating `docs/DATA.md`, `scripts/validate.py` and the tests together.
- Standard library only.

## Rules for every LITSA repo

- **No secrets.** Never write API keys, tokens or passwords into a file, a commit, an issue or a test. Keys come from environment variables. If you find one committed, stop and tell a maintainer.
- **No personal data.** No real names, emails, student records, sign-in sheets or mailing lists in code, tests, fixtures, screenshots or commit messages. Use made-up examples (`jane.doe@example.edu`).
- **No invented law.** Anything stating a rule, statute, case or requirement must come from a source you can link. Never make up a citation. If you can't find the source, say so in the pull request instead of guessing.
- **Small changes.** One issue per pull request. Don't reformat or rename things the issue didn't ask about.
- **Run the checks** listed above before saying the work is done, and report what they printed. If one fails, fix it or say plainly that it fails.
- **Plain writing.** Docs and messages use short, ordinary sentences a first-year law student would follow.
- **Disclose AI use.** The person opening the pull request notes which AI tools helped, in the description. They own every line either way.
