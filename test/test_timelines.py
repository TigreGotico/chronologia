"""Gold tests for civil timelines and their discontinuities.

Gold values are the documented skipped-label lists and dual dates of the
Gregorian-adoption family, cross-checked against the JDN hub.  Sources are
cited per case (see ``chronologia/timelines.py``).

Per-timeline gold summary
-------------------------
* rome_1582 — day after Julian 4 Oct 1582 is Gregorian 15 Oct 1582; labels
  5–14 Oct 1582 never existed (Wikipedia, "Adoption of the Gregorian calendar").
* britain_1752 — Julian 2 Sep 1752 followed by Gregorian 14 Sep 1752 (SKIP
  3–13 Sep); civil year turned over 25 March until 1752, so "24 Feb 1731" is
  astronomical Julian 1732, dual-dated 1731/32
  (Wikipedia, "Calendar (New Style) Act 1750", "Old Style and New Style dates").
* russia_1918 — the October Revolution: 25 Oct 1917 (Julian in force) is the
  same instant as proleptic Gregorian 7 Nov 1917; SKIP 1–13 Feb 1918
  (Wikipedia, "Adoption of the Gregorian calendar").
* greece_1923 — SKIP 16–28 Feb 1923 (Wikipedia, "Adoption of the Gregorian calendar").
* sweden_1700_1712 — the double leap day 30 Feb 1712 exists and is the day
  Gregorian calls 1712-03-11 (Wikipedia, "Swedish calendar").
* japan_1873 — switch at Meiji 6 = 1 Jan 1873; pre-1873 lunisolar segment is
  out of the registry (Wikipedia, "Japanese calendar").
"""
import pytest

from chronologia.calendars import (gregorian_to_jdn, jdn_to_gregorian,
                                    julian_to_jdn)
from chronologia.timelines import (TIMELINES, CivilLabel, DiscontinuityKind,
                                    NeverExisted, OutOfTimeline, Timeline,
                                    TimelineSegment, Discontinuity,
                                    UnknownCalendar, proleptic)


# --------------------------------------------------------------------------
# rome_1582
# --------------------------------------------------------------------------

def test_rome_last_julian_day_and_next_gregorian_label():
    r = TIMELINES["rome_1582"]
    last_julian = julian_to_jdn(1582, 10, 4)
    assert r.from_jdn(last_julian) == CivilLabel(1582, 10, 4)
    # the very next JDN is labelled 15 October 1582, not the 5th
    assert r.from_jdn(last_julian + 1) == CivilLabel(1582, 10, 15)


def test_rome_skipped_label_never_existed():
    r = TIMELINES["rome_1582"]
    result = r.to_jdn((1582, 10, 9))
    assert isinstance(result, NeverExisted)
    assert result.discontinuity.kind is DiscontinuityKind.SKIP
    assert result.discontinuity.before_label == CivilLabel(1582, 10, 4)
    assert result.discontinuity.after_label == CivilLabel(1582, 10, 15)


def test_rome_seam_is_one_day_wide_in_jdn():
    r = TIMELINES["rome_1582"]
    # duration math is JDN-space: 4 Oct and 15 Oct 1582 are one day apart
    assert r.to_jdn((1582, 10, 15)) - r.to_jdn((1582, 10, 4)) == 1


def test_rome_group_aliases_share_the_timeline():
    for key in ("spain_1582", "portugal_1582", "italy_1582", "poland_1582"):
        assert TIMELINES[key] is TIMELINES["rome_1582"]


# --------------------------------------------------------------------------
# britain_1752
# --------------------------------------------------------------------------

def test_britain_september_skip():
    b = TIMELINES["britain_1752"]
    seam = gregorian_to_jdn(1752, 9, 14)
    assert b.from_jdn(seam - 1) == CivilLabel(1752, 9, 2)
    assert b.from_jdn(seam) == CivilLabel(1752, 9, 14)


def test_britain_relabel_year_start_dual_dating():
    b = TIMELINES["britain_1752"]
    # "24 February 1731" old reckoning: month before 25 March => civil year is
    # the previous number, i.e. astronomical Julian 1732 (dual date "1731/32").
    jdn = b.to_jdn((1731, 2, 24))
    assert jdn == julian_to_jdn(1732, 2, 24)
    assert b.from_jdn(jdn) == CivilLabel(1731, 2, 24)
    # dual dating: civil 1731, astronomical (Julian) 1732
    from chronologia.calendars import jdn_to_julian
    assert jdn_to_julian(jdn)[0] == 1732


def test_britain_relabel_discontinuity_short_year_1751():
    b = TIMELINES["britain_1752"]
    relabels = [d for d in b.discontinuities
                if d.kind is DiscontinuityKind.RELABEL]
    assert len(relabels) == 1
    # 1751 ran 25 March – 31 December, so its last civil day is 31 Dec 1751 and
    # the next civil label is 1 Jan 1752.
    assert relabels[0].before_label == CivilLabel(1751, 12, 31)
    assert relabels[0].after_label == CivilLabel(1752, 1, 1)


# --------------------------------------------------------------------------
# russia_1918 — the October Revolution
# --------------------------------------------------------------------------

def test_russia_october_revolution_label_jdn_gregorian():
    ru = TIMELINES["russia_1918"]
    jdn = julian_to_jdn(1917, 10, 25)      # 25 Oct 1917, Julian in force
    assert ru.from_jdn(jdn) == CivilLabel(1917, 10, 25)
    assert ru.to_jdn((1917, 10, 25)) == jdn
    # the same instant is proleptic Gregorian 7 November 1917
    assert jdn_to_gregorian(jdn) == (1917, 11, 7)
    assert proleptic("gregorian").from_jdn(jdn) == CivilLabel(1917, 11, 7)


def test_russia_february_1918_skip():
    ru = TIMELINES["russia_1918"]
    for day in range(1, 14):               # 1–13 February 1918 never existed
        assert isinstance(ru.to_jdn((1918, 2, day)), NeverExisted)
    assert ru.from_jdn(gregorian_to_jdn(1918, 2, 14)) == CivilLabel(1918, 2, 14)


# --------------------------------------------------------------------------
# greece_1923
# --------------------------------------------------------------------------

def test_greece_february_1923_skip():
    g = TIMELINES["greece_1923"]
    assert g.from_jdn(julian_to_jdn(1923, 2, 15)) == CivilLabel(1923, 2, 15)
    assert g.from_jdn(gregorian_to_jdn(1923, 3, 1)) == CivilLabel(1923, 3, 1)
    for day in range(16, 29):              # 16–28 February 1923 never existed
        assert isinstance(g.to_jdn((1923, 2, day)), NeverExisted)


# --------------------------------------------------------------------------
# sweden_1700_1712 — the double leap day
# --------------------------------------------------------------------------

def test_sweden_feb_30_1712_maps_to_real_jdn():
    sw = TIMELINES["sweden_1700_1712"]
    jdn = sw.to_jdn((1712, 2, 30))
    assert isinstance(jdn, int)
    assert jdn == gregorian_to_jdn(1712, 3, 11)     # verified vs the source
    assert sw.from_jdn(jdn) == CivilLabel(1712, 2, 30)


def test_sweden_1753_gregorian_adoption_skip():
    sw = TIMELINES["sweden_1700_1712"]
    for day in range(18, 29):              # 18–28 February 1753 never existed
        assert isinstance(sw.to_jdn((1753, 2, day)), NeverExisted)
    assert sw.from_jdn(gregorian_to_jdn(1753, 3, 1)) == CivilLabel(1753, 3, 1)


# --------------------------------------------------------------------------
# japan_1873 — out-of-registry pre-switch segment
# --------------------------------------------------------------------------

def test_japan_switch_and_out_of_registry_segment():
    jp = TIMELINES["japan_1873"]
    assert jp.from_jdn(gregorian_to_jdn(1873, 1, 1)) == CivilLabel(1873, 1, 1)
    # pre-1873 the lunisolar calendar is not in the registry
    with pytest.raises(UnknownCalendar):
        jp.from_jdn(gregorian_to_jdn(1870, 1, 1))
    with pytest.raises(OutOfTimeline):
        jp.to_jdn((1870, 1, 1))
    switch = [d for d in jp.discontinuities][0]
    assert switch.after_label == CivilLabel(1873, 1, 1)


# --------------------------------------------------------------------------
# proleptic timelines behave identically to the raw calendar
# --------------------------------------------------------------------------

@pytest.mark.parametrize("cal", ["gregorian", "julian"])
def test_proleptic_matches_raw_calendar(cal):
    from chronologia.calendars import (gregorian_to_jdn, jdn_to_gregorian,
                                       julian_to_jdn, jdn_to_julian)
    to = {"gregorian": gregorian_to_jdn, "julian": julian_to_jdn}[cal]
    frm = {"gregorian": jdn_to_gregorian, "julian": jdn_to_julian}[cal]
    tl = proleptic(cal)
    for (y, m, d) in [(1, 1, 1), (1582, 10, 9), (2000, 2, 29), (-44, 3, 15)]:
        jdn = to(y, m, d)
        assert tl.to_jdn((y, m, d)) == jdn
        assert tl.from_jdn(jdn) == CivilLabel(*frm(jdn))


def test_proleptic_has_no_discontinuities():
    assert proleptic("gregorian").discontinuities == ()


# --------------------------------------------------------------------------
# Adversarial cases
# --------------------------------------------------------------------------

def test_every_skip_window_label_never_existed():
    windows = {
        "rome_1582": [(1582, 10, d) for d in range(5, 15)],
        "britain_1752": [(1752, 9, d) for d in range(3, 14)],
        "russia_1918": [(1918, 2, d) for d in range(1, 14)],
        "greece_1923": [(1923, 2, d) for d in range(16, 29)],
        "sweden_1700_1712": [(1753, 2, d) for d in range(18, 29)],
    }
    for key, labels in windows.items():
        tl = TIMELINES[key]
        for label in labels:
            res = tl.to_jdn(label)
            assert isinstance(res, NeverExisted), (key, label, res)
            assert res.discontinuity.kind is DiscontinuityKind.SKIP


def test_out_of_segment_query_raises():
    # japan's only real segment is post-1873 Gregorian; a pre-segment label has
    # nowhere to go and is not inside a SKIP window.
    with pytest.raises(OutOfTimeline):
        TIMELINES["japan_1873"].to_jdn((1000, 5, 5))


def test_before_timeline_start_raises():
    from chronologia.timelines import _MIN_JDN
    with pytest.raises(OutOfTimeline):
        TIMELINES["rome_1582"].from_jdn(_MIN_JDN - 1)


def test_calendar_at_reports_calendar_in_force():
    r = TIMELINES["rome_1582"]
    assert r.calendar_at(julian_to_jdn(1582, 10, 4)) == "julian"
    assert r.calendar_at(gregorian_to_jdn(1582, 10, 15)) == "gregorian"


def test_repeat_yields_two_candidate_tuple():
    # A synthetic REPEAT: the same civil label is generated by two adjacent
    # segments (one label, two JDNs) — e.g. Alaska 1867's repeated day.
    from chronologia.timelines import _MIN_JDN
    greg = gregorian_to_jdn(1867, 10, 6)   # label 6 Oct while Gregorian in force
    jul = julian_to_jdn(1867, 10, 6)       # label 6 Oct while Julian in force
    assert greg < jul                      # same label, Julian lands later
    # Gregorian first, then the calendar is set back to Julian at the seam, so
    # the label "6 October 1867" is generated twice — once on each side.
    seam = greg + 1
    tl = Timeline(
        "alaska_1867",
        (TimelineSegment(_MIN_JDN, "gregorian"),
         TimelineSegment(seam, "julian")),
        (Discontinuity(seam, DiscontinuityKind.REPEAT,
                       (1867, 10, 6), (1867, 10, 6), "synthetic"),))
    result = tl.to_jdn((1867, 10, 6))
    assert isinstance(result, tuple)
    assert set(result) == {greg, jul}


def test_never_existed_is_not_an_exception():
    # the design: a non-existent label is a typed answer, never a raise
    res = TIMELINES["rome_1582"].to_jdn((1582, 10, 7))
    assert isinstance(res, NeverExisted)
    assert res.label == CivilLabel(1582, 10, 7)
