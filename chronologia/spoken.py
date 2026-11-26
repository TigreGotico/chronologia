"""The spoken form of a date, a clock time or a year.

Each function takes a BCP 47 tag. A lect tag (``pt-PT-x-lisbon``) falls back
to its base. The output is words only. The language rules are data in
``chronologia/locale/<lang>/spoken.json``, and every number word comes from
``numtag.spell``.

A language with no writer raises :class:`UnsupportedForm`, a ``ValueError``.
A value out of range or a date that does not exist raises ``ValueError``.
"""
import calendar
import json
import os
from functools import lru_cache
from typing import Optional

from numtag import SpokenForm, spell

from chronologia.version import VERSION_STR

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")


class UnsupportedForm(ValueError):
    """The language has no reading for this form, field, style or case."""

    def __init__(self, tag: str, form: str, detail: str):
        super().__init__(f"{tag}: no {form} reading for {detail}")
        self.tag = tag
        self.form = form
        self.detail = detail


def _base_tag(tag: str) -> tuple:
    """(language, region) of a tag, with the private-use part removed."""
    parts = tag.strip().replace("_", "-").split("-")
    if "x" in (p.lower() for p in parts):
        parts = parts[:[p.lower() for p in parts].index("x")]
    region = next((p.upper() for p in parts[1:]
                   if len(p) == 2 and p.isalpha()), None)
    return parts[0].lower(), region


@lru_cache(maxsize=None)
def _rules_for(language: str) -> Optional[dict]:
    path = os.path.join(_LOCALE_DIR, language, "spoken.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _rules(tag: str, form: str) -> tuple:
    """The writer data and the base tag that numtag reads."""
    language, region = _base_tag(tag)
    rules = _rules_for(language)
    key = language if region is None else f"{language}-{region}"
    if rules is None or key not in rules["tags"]:
        raise UnsupportedForm(tag, form, "this language")
    return rules, key


def writes(tag: str) -> bool:
    """True when chronologia has a date and time writer for the tag."""
    try:
        _rules(tag, "date")
    except UnsupportedForm:
        return False
    return True


def revision() -> str:
    """The version string of the writer data."""
    return VERSION_STR


def _number(value: int, tag: str, gender: str,
            form: SpokenForm = SpokenForm.CARDINAL) -> str:
    return spell(str(value), tag, form=form, gender=gender)[0].text


def _count(value: int, unit: str, gender: str, tag: str, rules: dict) -> str:
    singular, plural = rules["units"][unit]
    one = value == 1 or (value == 0 and not rules["zero_is_plural"])
    return f"{_number(value, tag, gender)} {singular if one else plural}"


def _check_year(year: int):
    if not 1 <= year <= 9999:
        raise ValueError(f"year {year} is outside 1 to 9999")


def _check_date(day, month, year, weekday):
    if day is None and month is None and year is None:
        raise ValueError("a date needs a day, a month or a year")
    if year is not None:
        _check_year(year)
    if month is not None and not 1 <= month <= 12:
        raise ValueError(f"month {month} is outside 1 to 12")
    if day is not None:
        if month is None and year is not None:
            raise ValueError("a day and a year need a month")
        # with no year, 29 February exists
        last = calendar.monthrange(year or 2000, month)[1] if month else 31
        if not 1 <= day <= last:
            raise ValueError(f"day {day} does not exist in month {month}")
    if weekday is not None:
        if day is None:
            raise ValueError("a weekday needs a day")
        if not 0 <= weekday <= 6:
            raise ValueError(f"weekday {weekday} is outside 0 to 6")
        if None not in (day, month, year) \
                and calendar.weekday(year, month, day) != weekday:
            raise ValueError("the weekday does not match the date")


def _refuse(tag: str, form: str, **marks):
    for name, value in marks.items():
        if value is not None:
            raise UnsupportedForm(tag, form, f"{name} {value!r}")


def spoken_date(tag: str, *, day: Optional[int] = None,
                month: Optional[int] = None, year: Optional[int] = None,
                weekday: Optional[int] = None, case: Optional[str] = None,
                declension: Optional[str] = None) -> str:
    """The spoken form of a full or partial date.

    A day alone gives the day reading, a month alone the month name.
    ``weekday`` is 0 for Monday, as ``datetime.weekday()``.
    """
    rules, base = _rules(tag, "date")
    _check_date(day, month, year, weekday)
    _refuse(tag, "date", case=case, declension=declension)
    words = []
    if day is not None:
        form = SpokenForm.ORDINAL if day in rules["day_ordinal"] \
            else SpokenForm.CARDINAL
        words.append(_number(day, base, rules["year_gender"], form))
    if month is not None:
        words.append(rules["months"][month - 1])
    if year is not None:
        words.append(_number(year, base, rules["year_gender"]))
    date = f" {rules['date_joiner']} ".join(words)
    if weekday is not None:
        date = f"{rules['weekdays'][weekday]} {date}"
    return date


def _day_period(hour: int, rules: dict) -> str:
    return [word for start, word in rules["day_periods"] if hour >= start][-1]


def _phrase(hour: int, minute: int, period: bool, tag: str,
            rules: dict) -> str:
    """The conversational 12-hour reading: "duas e meia da tarde"."""
    phrase = rules["phrase"]
    spoken_hour = hour
    if minute in phrase["before_minutes"]:
        minute -= 60
        spoken_hour = (hour + 1) % 24
    if spoken_hour == 0:
        speak = rules["midnight"]
    elif spoken_hour == 12:
        speak = rules["noon"]
    else:
        speak = _number(spoken_hour % 12, tag, rules["hour_gender"])
    if str(minute) in phrase["fractions"]:
        speak += " " + phrase["fractions"][str(minute)]
    elif minute > 0:
        speak += f" {rules['and']} " + _number(minute, tag,
                                               rules["count_gender"])
    elif minute < 0:
        speak += f" {phrase['before']} " + _number(-minute, tag,
                                                   rules["count_gender"])
    if minute == 0 and not period:
        speak += " " + phrase["on_the_hour"]
    if period and spoken_hour not in (0, 12):
        speak += " " + _day_period(hour, rules)
    return speak


def spoken_time(tag: str, hour: int, minute: int = 0,
                second: Optional[int] = None, *, clock: str = "24h",
                style: str = "digits", period: bool = False,
                case: Optional[str] = None) -> str:
    """The spoken form of a clock time.

    ``style`` is "digits" (the clock as numbers), "units" (with the words
    for hour, minute and second) or "phrase" (the 12-hour conversational
    reading). ``period`` says the part of the day on the 12h clock.
    """
    rules, base = _rules(tag, "time")
    if not 0 <= hour <= 23 or not 0 <= minute <= 59 \
            or (second is not None and not 0 <= second <= 59):
        shown = f"{hour}:{minute:02}" + (
            "" if second is None else f":{second:02}")
        raise ValueError(f"{shown} is not a clock time")
    if clock not in ("24h", "12h"):
        raise ValueError(f"unknown clock {clock!r}")
    if style not in ("digits", "units", "phrase"):
        raise ValueError(f"unknown style {style!r}")
    if period and clock != "12h":
        raise ValueError("a day period needs the 12h clock")
    _refuse(tag, "time", case=case)
    if style == "phrase":
        if clock != "12h" or second is not None:
            detail = f"the phrase style on the {clock} clock"
            raise UnsupportedForm(tag, "time", detail if second is None
                                  else detail + " with seconds")
        return _phrase(hour, minute, period, base, rules)
    shown = hour if clock == "24h" else hour % 12 or 12
    hours = _count(shown, "hour", rules["hour_gender"], base, rules)
    if style == "units":
        parts = [hours]
        if minute:
            parts.append(_count(minute, "minute", rules["count_gender"],
                                base, rules))
        if second is not None:
            parts.append(_count(second, "second", rules["count_gender"],
                                base, rules))
        joiner = f" {rules['and']} "
        speak = joiner.join(parts) if len(parts) < 3 \
            else f"{parts[0]} {parts[1]}{joiner}{parts[2]}"
    else:
        if second is not None:
            raise UnsupportedForm(tag, "time",
                                  f"the digits style on the {clock} clock"
                                  " with seconds")
        if minute:
            speak = _number(shown, base, rules["hour_gender"]) \
                + f" {rules['and']} " \
                + _number(minute, base, rules["count_gender"])
        else:
            speak = hours
    if clock == "12h" and period:
        if minute == 0 and second is None and hour in (0, 12):
            return rules["midnight"] if hour == 0 else rules["noon"]
        speak += " " + _day_period(hour, rules)
    return speak


def spoken_year(tag: str, year: int, *, ordinal: bool = False,
                case: Optional[str] = None,
                declension: Optional[str] = None) -> str:
    """The spoken form of a year from 1 to 9999."""
    rules, base = _rules(tag, "year")
    _check_year(year)
    if ordinal:
        raise UnsupportedForm(tag, "year", "an ordinal year")
    _refuse(tag, "year", case=case, declension=declension)
    return _number(year, base, rules["year_gender"])
