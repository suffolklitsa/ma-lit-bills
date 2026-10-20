# Data contract

`scripts/validate.py` enforces this in CI.

## `data/<court>/bills.json`

| Field | Type | Notes |
|---|---|---|
| `schema_version` | number | `1` |
| `court` | number | General Court, e.g. `194` |
| `documents_scanned` | number | How many documents the session had at fetch time |
| `bills` | list | One record per tracked bill |

### Bill record

| Field | Type | Example |
|---|---|---|
| `bill` | string | `H3444` (House) or `S2345` (Senate) |
| `docket` | string or null | `HD2050` |
| `court` | number | `194` |
| `title` | string | `An Act relative to ...` |
| `url` | string | `https://malegislature.gov/Bills/194/H3444` |
| `primary_sponsor` | string or null | |
| `cosponsor_count` | number | |
| `filed` | `YYYY-MM-DD` or null | First history date |
| `last_action` | object or null | `{date, branch, action}` |
| `history` | list | `{date, branch, action}`, oldest first; stricken entries removed. `date` can be null: the Legislature records some actions (study orders, clerk processing) without one. Undated actions come after dated ones. |
| `topics` | list of topic ids | From `topics/topics.toml` |
| `review` | string | `candidate` (matched, not yet checked) or `confirmed` (a person checked it) |
| `summary` | object or null | `{text, written_by, reviewed_by, reviewed_on}`. Confirmed bills only. |

## `data/<court>/review.toml`

```toml
[confirmed.H1234]
topics = ["ai"]          # optional; overrides title matching
reviewed_by = "Name"

[rejected.H5678]
reason = "Why it isn't a tech bill"
reviewed_by = "Name"
```

A bill can't be both confirmed and rejected.
