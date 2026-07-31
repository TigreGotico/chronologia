# Edge Case Analysis: chronologia/calendars.py and chronologia/recurrence.py

## Scope

Files analyzed:
- `/home/miro/AgentWorkspaces/ml/chronologia/chronologia/calendars.py` (17 calendars, JDN hub, `Calendar`/`TabulatedCalendar`/`CalendarDate` facades)
- `/home/miro/AgentWorkspaces/ml/chronologia/chronologia/recurrence.py` (RFC 5545 RRULE engine)

Not a full repo audit; these two files were explicitly out of scope of prior audits. All findings below were reproduced live with
`PYTHONPATH=/home/miro/AgentWorkspaces/ml/chronologia ~/.venvs/ovos/bin/python3 -c "..."`.

## Summary

Two genuine contract violations were reproduced: (1) `CalendarDate.astro` (and any code path that builds a `CalendarDate` directly, including `from_json`) silently fabricates a plausible-looking but wrong Gregorian instant for an impossible calendar date, because it calls `cal.to_jdn` directly without the `validate()` gate that `Calendar.date()` uses — this is exactly the "silent-wrong" failure the module's own `_validate_fields` docstring says it exists to prevent, just reachable through a different door; (2) `Recurrence` with `COUNT=0` (explicitly permitted by `_validate`, which only rejects `count < 0`) still emits exactly one occurrence instead of zero, because the `count` cutoff is checked after the `yield`. All other explored edge cases (impossible BYMONTH/BYMONTHDAY combinations, BYMONTHDAY=31/-1 in short months, BYMONTH=2;BYMONTHDAY=29, UNTIL before DTSTART, BYDAY ordinal 0, proleptic negative years, ISO week 53 in a non-53-week year, tabulated-calendar `validate()`) were verified to behave correctly (clean `ValueError` or clean empty/filtered result).

| Priority | Count |
|----------|-------|
| Critical | 1     |
| High     | 1     |
| Medium   | 0     |
| Low      | 1     |

Full analysis written to: /home/miro/AgentWorkspaces/ml/chronologia/edge-case-analysis.md

## Input Source Map

| Input | Origin | Type | Validated? |
|-------|--------|------|------------|
| `CalendarDate(calendar, year, month, day)` | Any caller (direct construction, or `CalendarDate.from_json` deserializing untrusted JSON) | dataclass of raw ints | No — `.astro` calls `cal.to_jdn` directly, bypassing `Calendar.validate()` |
| `Calendar.date(year, month, day)` | Library-recommended entry point | ints | Yes — calls `self.validate()` first |
| `Recurrence.count` / `count=` override | `parse_rrule` (untrusted `RRULE:` string) or `every(count=...)` | int | Only bounds-checked for `< 0` and `> _MAX_COUNT`; `0` is accepted as legal but mishandled during expansion |
| `to_jdn`/`from_jdn` module-level functions (`islamic_civil_to_jdn`, `hebrew_to_jdn`, `french_republican_to_jdn`, `bahai_to_jdn`, ...) | Called directly by any code that imports the module (not just through `Calendar`) | raw ints, no bounds | No — documented as "pure arithmetic", validation is layered on top by `_validate_fields`/`Calendar.validate()`, not by the functions themselves |
| `BYMONTHDAY`/`BYMONTH`/`BYDAY` ordinal | `parse_rrule` string or `every(...)` kwargs | ints/strings | Yes — `_validate` rejects impossible fixed combinations (e.g. `BYMONTH=2;BYMONTHDAY=30`) and per-field ranges |

## Findings

**EC1: `CalendarDate.astro` silently fabricates a wrong Gregorian instant for an impossible calendar date**
- **Priority:** Critical
- **Dimension:** Boundary values / error propagation (validation bypass)
- **Input:** `CalendarDate(calendar, year, month, day)` constructed directly or via `CalendarDate.from_json` (both public, both reachable with untrusted data), then `.astro` accessed
- **Scenario:** Any impossible `(year, month, day)` for the named calendar — verified with:
  - `CalendarDate('islamic_civil', 1445, 9, 31)` (Ramadan, an odd/30-day month, has no day 31) → `.astro` = `2024-04-10` (silently shifted into month 10)
  - `CalendarDate.from_json({'calendar': 'hebrew', 'year': 5785, 'month': 13, 'day': 1})` (5785 is NOT a Hebrew leap year, so month 13/Adar II does not exist) → `.astro` = `2025-03-30`
  - `CalendarDate('french_republican', 5, 0, 1)` (month 0 does not exist; months are 1..13) → `.astro` = `1796-08-23`
  - `CalendarDate('bahai', 100, 0, 6)` (Ayyám-i-Há day 6; the intercalary period is only 4 or 5 days) → `.astro` = `1944-03-02`
- **Code location:** `chronologia/calendars.py:932-938` (`CalendarDate.astro` calls `cal.to_jdn(...)` with no validation), contrast with `chronologia/calendars.py:1184-1196` (`Calendar.date()` calls `self.validate(...)` first) and `:842-848` (`_accepts`, the round-trip check that `validate()` uses but `.astro` does not)
- **Current handling:** None on the `CalendarDate`/`.astro` path. `Calendar.validate()`/`Calendar.date()` (a different call path) correctly rejects the same inputs with `ValueError` — reproduced live: `CALENDARS['hebrew'].validate(5785, 13, 1)` raises `"hebrew month 13 out of range for year 5785; expected 1..12"`, and `CALENDARS['islamic_civil'].validate(1445, 9, 31)` raises `"islamic_civil day 31 out of range for 1445-9; expected 1..30"`.
- **Expected behavior:** `CalendarDate.astro` (and `TabulatedCalendar`/`Calendar` round-trips reached through a bare `CalendarDate`) should validate before converting, or `CalendarDate.__post_init__` should validate at construction time, so an impossible date either raises or is otherwise flagged rather than silently producing a wrong-but-plausible Gregorian instant.
- **Risk:** Silent data corruption — this is precisely the "confident, plausible-looking — and wrong" failure mode the module's own `_validate_fields` docstring (`calendars.py:865-871`) identifies as the thing validation exists to prevent, but `CalendarDate`/`from_json` is an unguarded second entry point to the exact same arithmetic. Any caller that round-trips a `CalendarDate` through JSON (the documented `to_json`/`from_json` envelope) and then reads `.astro` gets silently wrong dates for malformed/corrupted data with no signal at all.

**EC2: `Recurrence` with `COUNT=0` emits one occurrence instead of zero**
- **Priority:** High
- **Dimension:** Boundary values (numeric zero) / error propagation (off-by-one in the cutoff check)
- **Input:** `every('daily', count=0)` (or `parse_rrule('FREQ=DAILY;COUNT=0')`), expanded via `occurrences(rec, dtstart)`
- **Scenario:** `_validate` at `chronologia/recurrence.py:296-297` only rejects `count < 0`, so `count=0` is accepted as a legal, deliberately-supported value (distinct from `count=None`/unbounded). Live: `len(list(occurrences(every('daily', count=0), AstroDate(2024,1,1))))` returns `1`, identical to `count=1`.
- **Code location:** `chronologia/recurrence.py:748-764` — inside the innermost loop, `emitted += 1` then `yield span` happen *before* the `emitted >= eff_count` cutoff is checked, so the first candidate is always yielded even when `eff_count == 0`.
- **Current handling:** None — the cutoff check `if eff_count is not None and emitted >= eff_count: return` (line 763-764) runs only after the yield already happened for that item.
- **Expected behavior:** `COUNT=0` (or `count=0` override) should yield an empty iterator with zero occurrences, matching the ordinary meaning of "repeat 0 times" and the fact that `_validate` treats `0` as distinct from a rejected negative value (implying it is intentionally supported, not merely tolerated).
- **Risk:** A caller that computes a recurrence count dynamically (e.g. "remaining occurrences left in a quota") and legitimately arrives at `count=0` gets one unwanted occurrence instead of none — silently wrong output count, not a crash, so easy to miss in review.

**EC3: Module-level `*_to_jdn`/`*_from_jdn` functions perform no bounds checking at all (documented behavior, but a footgun for direct callers)**
- **Priority:** Low
- **Dimension:** Boundary values / API surface
- **Input:** Any direct caller of `islamic_civil_to_jdn`, `hebrew_to_jdn`, `french_republican_to_jdn`, `bahai_to_jdn`, etc. (bypassing the `Calendar` wrapper entirely)
- **Scenario:** e.g. `islamic_civil_to_jdn(1445, 0, 1)` (month 0) → JDN `2460116` → `islamic_civil_from_jdn` gives back `(1444, 12, 1)`, a different, wrong-looking date, with no exception. Same for day 0, negative days, and out-of-range months across every arithmetic calendar tested (islamic_civil, hebrew, french_republican, bahai).
- **Code location:** e.g. `chronologia/calendars.py:146-171` (`_abs_from_islamic`/`_islamic_from_abs`), `:230-259` (Hebrew), `:298-319` (French Republican), `:337-365` (Bahá'í) — none of these functions validate their inputs; validation is intentionally centralized in `_validate_fields`/`Calendar.validate()` (module docstring at `:823-838`).
- **Current handling:** By design, none at this layer — the module explicitly documents that bounds live in `_validate_fields`, derived from the round-trip law, and are enforced by `Calendar.validate()`/`Calendar.date()`. This is a reasonable internal architecture; it becomes a real bug only via EC1's `CalendarDate` bypass.
- **Expected behavior:** No change needed here in isolation — flagged only because it is the shared root cause of EC1 and worth knowing about if any *other* future call site (besides `CalendarDate.astro`) is added that calls a bare `*_to_jdn` function without routing through `Calendar.validate()`.
- **Risk:** Low on its own since it's an internal/documented layering choice; the risk fully materializes only through EC1.

## Coverage Summary

- Total edge cases discovered: 3 (1 Critical, 1 High, 1 Low)
- Edge cases already tested: unable to find existing test files for these two modules during this focused pass beyond what's implied by the round-trip-based `_validate_fields` design itself (not separately inspected — see note below); no existing test appears to cover `CalendarDate.astro`/`from_json` on invalid input or `Recurrence(count=0)`, since both reproduce cleanly as bugs.
- Edge cases already handled in code but not tested: none found — `Calendar.validate()`'s correct rejection of bad input (Hebrew month 13 in a non-leap year, ISO week 53 in 2021, Islamic day 31 of Ramadan) was itself verified live and is correct; it is the *other* path (`CalendarDate.astro`) that is unhandled.
- Edge cases with no handling and no tests (highest risk): EC1 (`CalendarDate.astro` validation bypass) and EC2 (`COUNT=0` off-by-one).
- Dimensions not actively hunted in this focused pass: 3E (state dependencies / races) and 3C (cross-service integration boundaries) — this module is pure in-process arithmetic with no I/O, shared mutable state, or network calls (the only "integration point," `_load_tabulated`'s file read and the optional `_EVENT_PROVIDERS` registry, was read but not adversarially fuzzed with malformed `.tab` files, since that data ships with the package rather than arriving from an untrusted caller). 3B (external-input messiness in the SQL-injection/XSS sense) does not apply — every input here is Python ints/strings already parsed, not raw text reaching a shell/DB/HTML sink.

## Dropped Edge Cases

- **Fuzzing corrupt `calendar_data/*.tab` files** — `_load_tabulated` is called only at import time against files shipped inside the package itself, not against caller-supplied paths; no real caller can inject a malformed table without already having filesystem write access to the installed package, which is a different threat model than this library's documented contract.
- **`datetime.MINYEAR`/`MAXYEAR` boundary in `_as_astro`** — `recurrence.py`'s `_as_astro` reads `.year/.month/.day` off any duck-typed object and never touches `datetime.MINYEAR`/`MAXYEAR` itself (the module docstring explicitly states there is no `datetime` window and nothing overflows, since expansion is JDN-integer math); the only place stdlib `datetime` limits could matter is inside `AstroDate` construction, which lives in `astrodate.py`, not the two files in scope.
- **DST/timezone-naive assumptions** — recurrence's `UNTIL` cutoff is explicitly documented as a naive wall-clock comparison (module docstring, `_parse_until`); there is no timezone-aware code path anywhere in either file to misbehave, so there is no realistic "DST edge case" to trigger here (would apply to a tz-aware layer elsewhere, out of scope).
