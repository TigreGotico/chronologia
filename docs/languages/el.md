# Greek (`el`)

The week starts on Monday, dates are little-endian (`5 Ιουνίου 2020`), and the
locale prefers the future reading for an ambiguous bare time or date. Greek is
postpositional for its relative determiners on weekdays and the `rel_period`
construction — `την περασμένη Τρίτη`, the past Tuesday — so both carry an
`article? REL_MARKER article? WEEKDAY`/`UNIT` shape rather than a leading
marker.

## What ships

**Day parts** are four bands transcribed from the Unicode CLDR 47 day-period
rules for `el`: `πρωί` `[04:00, 12:00)`, `απόγευμα` `[12:00, 17:00)`, `βράδυ`
`[17:00, 20:00)` and `νύχτα` `[20:00, 04:00)` (crossing midnight). Each noun's
gender and its accusative article are confirmed against its own Wiktionary
lemma: `πρωί`, `απόγευμα` and `βράδυ` are neuter (`το`), `νύχτα` is feminine
(`τη`, since it begins with a consonant outside the vowel/plosive set that
forces `την`) — see the citations in `chronologia/locale/el/marker_article.voc`
and each `daypart_*_el.voc` file. The same four nouns double as clock
meridiem cues on an explicit hour: `πρωί` is a no-op AM confirmation,
`απόγευμα` and `βράδυ` are a uniform +12 PM shift, and `νύχτα` routes through
the shared midnight-crossing night-meridiem split (small hours 1–5 stay AM,
6–11 are PM, twelve is midnight) — see `chronologia/locale/el/
clock_meridiem_{am,pm,night}.voc`.

**Recurrence is unimplemented.** `κάθε μέρα` ("every day") does not resolve;
`marker_every.voc` ships the connector word but no construction consumes it
yet, so a sentence built on `κάθε` binds only the temporal fragment it happens
to contain (a daypart, a clock time) and strands `κάθε` in the remainder.

**The clock** ships the feminine clock-hour numerals that agree with the
elided `ώρα` (`τρεις`, `τέσσερις`, `μία`), the idiomatic `και μισή`/`και
τέταρτο` (past) and `παρά τέταρτο` (to) fractions, digit times, and the
`μεσημέρι`/`μεσάνυχτα` landmarks. Unlike the Continental-Germanic half hour,
Greek `και μισή` names the half *past* the stated hour, so no
`bare_half_to` trap applies.

**Quantifiers** ship `ένα`/`μια`/`μία`/`έναν` for one, `ζευγάρι` for a pair,
`μερικά`/`μερικές` for a few, and the fraction words `μισή`/`μισό`,
`τέταρτο` and `μιάμιση`.

## Open questions for a native speaker

1. Does `βράδυ` genuinely extend as a colloquial PM clock cue past its own
   CLDR band into the 21:00–23:00 hours (`εννιά/δέκα/έντεκα το βράδυ`), the
   way `tarde` does in Spanish and `abends` does in German, or does ordinary
   speech switch to `νύχτα` earlier than that?
2. Does the shared 5|6 hour cut used for the `νύχτα` night-meridiem split
   (small hours 1–5 read AM, 6–11 read PM) match how a Greek speaker actually
   parses an hour said with `νύχτα`, or does the boundary sit somewhere else
   in ordinary usage?
