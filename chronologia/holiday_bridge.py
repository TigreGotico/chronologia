"""Civil holidays — an optional bridge onto the ``holidays`` database.

Chronologia owns *rules*: arithmetic that anyone with the definition can
reproduce forever.  Easter is a computus; Christmas is a fixed December date;
the Islamic, Hebrew and Chinese feast anchors are calendar conversions off the
JDN hub.  None of that needs a database — it needs a formula, and formulae are
what the calendar registry, era, recurrence and computus layers already carry.

Civil holidays are the *other* half: which of those anchors a particular state
actually closes its offices for, plus the parts that are pure decree — founding
days, in-lieu ("bridge"/substitute) days, subdivision quirks, one-off royal
proclamations.  That half is not arithmetic; it is *data*, it changes every
few years by government gazette, and keeping it current is a full-time database
project.  The `vacanza/holidays <https://github.com/vacanza/holidays>`_ package
is that project.

So this module is the **tzdb pattern** applied to holidays: the way
:mod:`chronologia.zone_timelines` delegates the fast-moving offset database to
:mod:`zoneinfo` while owning the typed *timeline* semantics, this module
delegates the fast-moving observance database to ``holidays`` while owning the
typed :class:`Holiday` / :class:`~chronologia.astrodate.DateSpan` semantics.
Chronologia keeps the rules; the bridge borrows the decrees.

Division of labour
------------------
* **Arithmetic rules → chronologia.** Easter and the movable feasts hung off
  it, fixed-date feasts, and the calendar conversions that place Eid, Rosh
  Hashanah or the Spring Festival — anything a computus or a recurrence rule
  reproduces from a definition. These live in the computus / recurrence /
  calendar-registry layers and carry ``basis="exact"`` or ``"tabulated"``.
* **Observance data → the bridge.** Which anchors a country observes, plus
  proclamations, in-lieu substitute days and subdivision specifics — the parts
  that exist only because a government said so. These come from ``holidays``.

Optional dependency
-------------------
``holidays`` is **not** a runtime dependency of chronologia's core.  It is an
extra: ``pip install chronologia[holidays]``.  Every entry point here imports
it lazily inside the function body, so importing this module never drags the
database in, and a missing install fails with a clear, actionable message
rather than a bare :class:`ModuleNotFoundError`.

The honesty layer
-----------------
Lunar and Islamic-calendar observances cannot be known far ahead: the date a
country will *observe* Eid depends on a moon sighting or a future gazette, so
``holidays`` computes those forward dates from an arithmetic model and **flags
them as estimates**.  In v0.101 the flag rides in the holiday *name*: an
estimated entry is wrapped with the locale's ``estimated_label`` template
(``"%s (estimated)"`` in English, ``"%s (تقديري)"`` in Arabic, and so on), and
in-lieu days off an estimate use ``observed_estimated_label``
(``"%s (observed, estimated)"``).  Countries that publish an official forward
calendar — Saudi Arabia ships the Umm al-Qura calendar years ahead — set their
``_islamic_calendar_show_estimated`` flag off and are therefore *not* wrapped.

This bridge reads that flag and maps it onto chronologia's ``basis`` axis:

* wrapped (estimated) → ``basis="predicted"`` — a forward model, not a fact;
* not wrapped (confirmed past date, or an officially published calendar) →
  ``basis="tabulated"`` — a deterministic table that may still differ from a
  future observation, which is exactly what ``tabulated`` means.

Detection is done against the *object's own* translated label templates
(:meth:`HolidayBase.tr` applied to ``estimated_label`` /
``observed_estimated_label``), never a hard-coded English ``"(estimated)"``
substring — so it holds in every locale — and the marker is stripped back off
the name so :attr:`Holiday.name` is the clean observance name.

Multi-day observances
--------------------
``holidays`` emits every observed calendar day as its own dated entry: a
four-day Eid is four entries, and an in-lieu substitute ("bridge") day is a
*separate* dated entry from the holiday it compensates.  This bridge passes
them through one-to-one — each dated entry becomes one :class:`Holiday`,
day-wide — so a caller iterating :func:`civil_holidays` sees exactly the days
that are off, with the in-lieu days visible as their own spans.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date as _date
from datetime import timedelta as _timedelta
from typing import Iterable, Optional, Tuple, Union

from chronologia.astrodate import AstroDate, DateSpan

__all__ = ["Holiday", "civil_holidays", "is_holiday", "HolidaysNotInstalled"]

_INSTALL_HINT = (
    "the 'holidays' database is required for chronologia's civil-holiday "
    "bridge but is not installed. It is an optional extra — install it with:\n"
    "    pip install chronologia[holidays]\n"
    "(chronologia's core keeps no runtime dependency on it.)"
)


class HolidaysNotInstalled(ImportError):
    """Raised when the optional ``holidays`` extra is not installed."""


def _load_holidays():
    """Import the optional ``holidays`` package or fail with a clear hint.

    Imported lazily so that merely importing :mod:`chronologia.holiday_bridge`
    never pulls the database in, mirroring how the core stays dependency-free.
    """
    try:
        import holidays  # noqa: F401  (imported for its side of the bridge)
    except ImportError as exc:  # pragma: no cover - exercised via monkeypatch
        raise HolidaysNotInstalled(_INSTALL_HINT) from exc
    return holidays


@dataclass(frozen=True)
class Holiday:
    """One observed civil holiday, as chronologia's typed result.

    :attr:`span` is a **day-wide** :class:`~chronologia.astrodate.DateSpan`
    ``[that day 00:00, next day 00:00)`` whose ``basis`` carries the honesty
    signal (see the module docstring): ``"tabulated"`` for a confirmed or
    officially-published date, ``"predicted"`` for a model-estimated future
    lunar date.  :attr:`basis` is that same value, surfaced directly for
    convenience.
    """

    name: str
    span: DateSpan
    country: str
    subdiv: Optional[str]
    categories: Tuple[str, ...]
    basis: str

    @property
    def date(self) -> _date:
        """The civil date this holiday falls on, as a :class:`datetime.date`."""
        return _date(self.span.start.year, self.span.start.month,
                     self.span.start.day)


def _day_span(d: _date, basis: str) -> DateSpan:
    """A day-wide ``[d, d+1)`` :class:`DateSpan` carrying ``basis``."""
    start = AstroDate(d.year, d.month, d.day)
    end = start + _timedelta(days=1)
    return DateSpan(start, end, basis=basis)


def _marker_affixes(template: str) -> Optional[Tuple[str, str]]:
    """Split a ``"%s ..."`` label template into ``(prefix, suffix)`` or ``None``."""
    if "%s" not in template:
        return None
    prefix, suffix = template.split("%s", 1)
    return prefix, suffix


def _estimated_affixes(obj) -> Tuple[Tuple[str, str], ...]:
    """The translated estimate-marker affix pairs active on ``obj``.

    Reads the object's own ``estimated_label`` and ``observed_estimated_label``,
    translated into its active locale via :meth:`HolidayBase.tr`, so detection
    is language-independent (the English build wraps with ``"(estimated)"``, the
    Arabic build with ``"(تقديري)"``, etc.).
    """
    affixes = []
    for attr in ("estimated_label", "observed_estimated_label"):
        template = getattr(obj, attr, None)
        if not template:
            continue
        pair = _marker_affixes(obj.tr(template))
        if pair and (pair[0] or pair[1]):
            affixes.append(pair)
    return tuple(affixes)


def _strip_estimate(name: str, affixes) -> Tuple[str, bool]:
    """Return ``(clean_name, is_estimated)`` by peeling any estimate marker.

    Tries the longer-suffix markers first so ``"(observed, estimated)"`` is not
    mistaken for a bare ``"(estimated)"`` and half-stripped.
    """
    ordered = sorted(affixes, key=lambda pf: len(pf[0]) + len(pf[1]),
                     reverse=True)
    for prefix, suffix in ordered:
        if name.startswith(prefix) and name.endswith(suffix) \
                and len(name) > len(prefix) + len(suffix):
            inner = name[len(prefix):len(name) - len(suffix)] if suffix \
                else name[len(prefix):]
            return inner, True
    return name, False


def _resolve_categories(categories) -> Optional[Tuple[str, ...]]:
    """Normalise the ``categories`` argument to a tuple, or ``None``."""
    if categories is None:
        return None
    if isinstance(categories, str):
        return (categories,)
    return tuple(categories)


def civil_holidays(country: str, year: int, subdiv: Optional[str] = None,
                   categories: Optional[Union[str, Iterable[str]]] = None,
                   language: Optional[str] = None) -> Tuple[Holiday, ...]:
    """The civil holidays a country observes in ``year``, as typed objects.

    :param country: ISO-3166 alpha-2 country code (``"US"``, ``"DE"``, ...).
    :param year: the civil (Gregorian) year to enumerate.
    :param subdiv: optional subdivision code (``"CA"`` for California) whose
        state/province-specific observances are folded in.
    :param categories: optional category or categories to include
        (``"public"``, ``"government"``, ``"bank"``, ...); when given, each
        holiday's :attr:`~Holiday.categories` reflects exactly which of the
        requested categories claim it.  When omitted, the country's default
        category set is used.
    :param language: optional locale for the holiday names.
    :returns: a tuple of :class:`Holiday`, ordered by date; multi-day feasts
        and in-lieu substitute days appear as separate entries (see the module
        docstring).

    Raises :class:`HolidaysNotInstalled` if the optional extra is absent.
    """
    holidays = _load_holidays()
    wanted = _resolve_categories(categories)

    # Query one category at a time so each entry records the real category
    # (or categories) that claim it, rather than a single query-wide set.
    query_cats = wanted if wanted is not None else (None,)

    # date -> {name: set(category)} ; name here is the *clean* (unwrapped) name.
    collected: dict = {}
    predicted: dict = {}  # (date, clean_name) -> bool estimated
    for cat in query_cats:
        obj = holidays.country_holidays(
            country, subdiv=subdiv, years=year, language=language,
            categories=[cat] if cat is not None else None,
        )
        affixes = _estimated_affixes(obj)
        cat_label = cat if cat is not None else (
            next(iter(obj.categories)) if obj.categories else "public")
        for d, raw_name in obj.items():
            clean, estimated = _strip_estimate(raw_name, affixes)
            key = (d, clean)
            collected.setdefault(key, set()).add(cat_label)
            predicted[key] = predicted.get(key, False) or estimated

    result = []
    for (d, name), cats in collected.items():
        basis = "predicted" if predicted[(d, name)] else "tabulated"
        result.append(Holiday(
            name=name,
            span=_day_span(d, basis),
            country=country,
            subdiv=subdiv,
            categories=tuple(sorted(cats)),
            basis=basis,
        ))
    result.sort(key=lambda h: (h.date, h.name))
    return tuple(result)


def _as_date(value: Union[_date, AstroDate]) -> _date:
    """Coerce a :class:`datetime.date` or :class:`AstroDate` to a plain date."""
    if isinstance(value, AstroDate):
        return _date(value.year, value.month, value.day)
    if isinstance(value, _date):
        return value
    raise TypeError(
        f"is_holiday expects a datetime.date or AstroDate, got {type(value)!r}")


def is_holiday(date_or_astro: Union[_date, AstroDate], country: str,
               subdiv: Optional[str] = None,
               categories: Optional[Union[str, Iterable[str]]] = None,
               language: Optional[str] = None) -> Optional[Holiday]:
    """The :class:`Holiday` falling on a given day, or ``None``.

    Accepts either a :class:`datetime.date` or an
    :class:`~chronologia.astrodate.AstroDate` (so an astronomical anchor
    computed by the calendar layer can be checked directly).  When several
    observances share the date, the first by name is returned; enumerate the
    full day set with :func:`civil_holidays` if you need all of them.

    Raises :class:`HolidaysNotInstalled` if the optional extra is absent.
    """
    target = _as_date(date_or_astro)
    for holiday in civil_holidays(country, target.year, subdiv=subdiv,
                                  categories=categories, language=language):
        if holiday.date == target:
            return holiday
    return None
