"""Named-period registry: names for stretches of time, resolved to spans.

A :class:`NamedPeriod` binds a human name ("Jurassic", "Late Bronze Age") to a
:class:`~chronologia.astrodate.DateSpan`, tagged with a hierarchy *level*
(``eon``/``era``/``period``/``epoch``/``age`` for geology; ``period``/``age``
for the demonstrative archaeological set), an optional *region* (``None`` == a
global, region-independent name), a versioned *source*, and a *parent* key for
hierarchy walks.

Two data instances ship:

* the **ICS International Chronostratigraphic Chart** (version 2023/09) — the
  global deep-time scale, every eon/era/period/epoch/age with boundary ages in
  Ma placed on the Before-Present axis (AD 1950 epoch), published GSSP
  uncertainties folded outward into the endpoints, ``basis="tabulated"``;
* a **small, region-tagged archaeological set** (British three-age system vs
  Mesopotamian Bronze Age) that exists only to prove regional disambiguation —
  "Late Bronze Age" is a different span in Britain than in Mesopotamia, so a
  bare name is ambiguous and either takes a region tag or is listed by
  :func:`candidates`. Per-site phasings stay out.

Lookup is deliberately un-clever: :func:`lookup` answers an exact name (global)
or a ``(name, region)`` pair; resolving a bare, region-ambiguous name to a
locale default is the *consumer's* job, so this module gives it
:func:`candidates` to choose from rather than guessing.

:func:`subdivide` cuts *any* span into conventional early/mid/late thirds (or
first-/second-half), but a chart-defined subdivision wins: ``subdivide(
PERIODS["jurassic"], "late")`` returns the ICS **Late Jurassic** entry's span,
not an arithmetic third of the Jurassic.

:func:`calibrate_c14` bridges the ¹⁴C-BP and cal-BP reckonings through a coarse
IntCal20 sample — a demonstrative locator, never a substitute for OxCal.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from importlib import resources
from typing import List, Optional, Tuple, Union

from chronologia.astrodate import (AstroDate, DateSpan, combine_basis,
                                   BASIS_RECONSTRUCTED, BASIS_TABULATED)

_DATA_PACKAGE = "chronologia.data"

#: The Before-Present epoch: AD 1950 (Stuiver & Polach 1977), shared with the
#: deep-time machinery in :mod:`chronologia.eras`.
_BP_EPOCH_YEAR = 1950

#: ICS chart version embedded in :data:`PERIODS` (see the data file header).
ICS_CHART_VERSION = "2023/09"

_ICS_SOURCE = f"ICS International Chronostratigraphic Chart {ICS_CHART_VERSION}"

# Hierarchy rank, ascending width. Used to derive the geological parent of each
# chart entry by nominal-age containment, and to order candidate parents.
_LEVEL_RANK = {"age": 0, "epoch": 1, "period": 2, "era": 3, "eon": 4}


class AmbiguousPeriodError(KeyError):
    """A bare period name matches several region-tagged entries.

    Raised by :func:`lookup` when a name has no global (region-``None``) entry
    and more than one region-tagged candidate, since choosing a locale default
    is the consumer's responsibility. The offending candidates are available
    via :func:`candidates`.
    """


@dataclass(frozen=True, slots=True)
class NamedPeriod:
    """A named stretch of time bound to a :class:`DateSpan`.

    :param key: the registry key (lowercased name, region-suffixed when the
        name is region-tagged, e.g. ``"bronze_age_gb"``).
    :param name: the human-facing name ("Bronze Age").
    :param span: the interval the name denotes.
    :param level: hierarchy level — ``eon``/``era``/``period``/``epoch``/``age``.
    :param region: region tag (``"GB"``, ``"MESO"``) or ``None`` for a global,
        region-independent name (all ICS entries are global).
    :param source: the versioned authority the entry came from.
    :param parent: the key of the containing entry one level up, or ``None``.
    """
    key: str
    name: str
    span: DateSpan
    level: str
    region: Optional[str]
    source: str
    parent: Optional[str] = None


# --------------------------------------------------------------------------
# Before-Present axis helpers (deep-time entries)
# --------------------------------------------------------------------------
def _bp_astrodate(age_ma: Decimal, unc_ma: Decimal, older_edge: bool
                  ) -> AstroDate:
    """AstroDate for a boundary ``age_ma`` (± ``unc_ma``) million years ago.

    Uncertainty is folded *outward*: the older edge of a unit is pushed older
    (``age + unc``), the younger edge younger (``age - unc``), so the span
    covers the full published uncertainty envelope. Whole years step the
    astronomical year field exactly on the AD 1950 axis.
    """
    eff = age_ma + unc_ma if older_edge else age_ma - unc_ma
    years_before = int((eff * 1_000_000).to_integral_value(ROUND_HALF_UP))
    return AstroDate(_BP_EPOCH_YEAR - years_before, 1, 1)


def _load_lines(name: str):
    text = resources.files(_DATA_PACKAGE).joinpath(name).read_text()
    for line in text.splitlines():
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        yield line


def _load_ics() -> List[NamedPeriod]:
    # First pass: raw rows carrying nominal ages for parent derivation.
    raw = []  # (key, name, level, b_age, t_age, span)
    for line in _load_lines("ics_chart.tab"):
        parts = line.split("\t")
        if parts[0] == "key":  # header row
            continue
        key, name, level, b_age, t_age, b_unc, t_unc = parts
        span = DateSpan(
            _bp_astrodate(Decimal(b_age), Decimal(b_unc), older_edge=True),
            _bp_astrodate(Decimal(t_age), Decimal(t_unc), older_edge=False),
            basis=BASIS_TABULATED)
        raw.append((key, name, level, float(b_age), float(t_age), span))

    # Second pass: derive each entry's parent as the narrowest higher-rank
    # entry that contains it by NOMINAL age (chart units nest exactly by age;
    # nominal containment avoids the outward-folded uncertainty perturbing the
    # boundaries).
    periods = []
    for key, name, level, b_age, t_age, span in raw:
        rank = _LEVEL_RANK[level]
        parent = None
        best = None  # (rank, width) of the chosen parent
        for k2, n2, l2, b2, t2, s2 in raw:
            r2 = _LEVEL_RANK[l2]
            if r2 <= rank:
                continue
            if b2 >= b_age and t2 <= t_age:  # p contains e (ages: older=bigger)
                cand = (r2, b2 - t2)
                if best is None or cand < best:
                    best, parent = cand, k2
        periods.append(NamedPeriod(key, name, span, level, None,
                                   _ICS_SOURCE, parent))
    return periods


def _load_archaeo() -> List[NamedPeriod]:
    out = []
    for line in _load_lines("archaeo_periods.tab"):
        parts = line.split("\t")
        if parts[0] == "key":
            continue
        key, name, level, region, start, end, parent, basis = parts
        span = DateSpan(AstroDate(int(start), 1, 1), AstroDate(int(end), 1, 1),
                        basis=basis)
        out.append(NamedPeriod(
            key, name, span, level, region,
            f"Conventional archaeological chronology ({region})",
            None if parent == "-" else parent))
    return out


def _build_registry():
    reg = {}
    for p in _load_ics() + _load_archaeo():
        if p.key in reg:
            raise ValueError(f"duplicate period key {p.key!r}")
        reg[p.key] = p
    return reg


#: The named-period registry, keyed by :attr:`NamedPeriod.key`.
PERIODS = _build_registry()


# --------------------------------------------------------------------------
# Lookup
# --------------------------------------------------------------------------
def _norm(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def candidates(name: str) -> List[NamedPeriod]:
    """Every registry entry whose name matches ``name`` (any region).

    The disambiguation surface for a bare name: ``candidates("bronze age")``
    lists the British and Mesopotamian entries so a consumer can pick one by
    region or locale default. Matching is on the normalised name (case- and
    separator-insensitive), so ``"Late Jurassic"``, ``"late jurassic"`` and
    ``"late_jurassic"`` are equivalent. Returns ``[]`` for an unknown name.
    """
    target = _norm(name)
    return [p for p in PERIODS.values() if _norm(p.name) == target]


def lookup(name: str, region: Optional[str] = None) -> NamedPeriod:
    """Resolve a period name to its :class:`NamedPeriod`.

    With ``region``, matches the ``(name, region)`` entry exactly. Without it,
    returns the global (region-``None``) entry if one exists; if the name is
    only region-tagged, returns it when unambiguous and raises
    :class:`AmbiguousPeriodError` when several regions share it — resolving a
    bare ambiguous name to a locale default is the consumer's job (see
    :func:`candidates`).

    Also accepts a registry key directly (``lookup("late_jurassic")``).

    :raises KeyError: the name/region pair is unknown.
    :raises AmbiguousPeriodError: a bare name matches multiple regions.
    """
    if region is not None:
        target = _norm(name)
        for p in PERIODS.values():
            if p.region == region and (_norm(p.name) == target or p.key == name):
                return p
        raise KeyError(f"no period {name!r} for region {region!r}")

    # exact key hit first (unambiguous by construction)
    if name in PERIODS:
        return PERIODS[name]

    cands = candidates(name)
    globals_ = [p for p in cands if p.region is None]
    if globals_:
        return globals_[0]
    if not cands:
        raise KeyError(f"unknown period {name!r}")
    if len(cands) == 1:
        return cands[0]
    regions = sorted((p.region for p in cands), key=lambda r: r or "")
    raise AmbiguousPeriodError(
        f"{name!r} is region-ambiguous across {regions}; "
        f"pass region= or use candidates()")


def children(key: str) -> List[NamedPeriod]:
    """The registry entries whose :attr:`~NamedPeriod.parent` is ``key``."""
    return [p for p in PERIODS.values() if p.parent == key]


# --------------------------------------------------------------------------
# early / mid / late subdivision
# --------------------------------------------------------------------------
# Conventional-third and half operators. early/mid/late are thirds; the
# first-/second-half aliases are halves. "middle" is accepted for "mid".
_THIRDS = {"early": 0, "mid": 1, "middle": 1, "late": 2}
_HALVES = {"first_half": 0, "first-half": 0, "firsthalf": 0, "second_half": 1,
           "second-half": 1, "secondhalf": 1}
# part -> the ICS ordinal-word that names a chart subdivision, when one exists.
_CHART_WORD = {"early": "early", "mid": "middle", "middle": "middle",
               "late": "late"}


def _arithmetic_subdivide(span: DateSpan, part: str) -> DateSpan:
    part_key = part.strip().lower().replace(" ", "_")
    start_us = span.start._total_us()
    total = span._delta_us
    basis = combine_basis(span.basis)
    if part_key in _THIRDS:
        idx = _THIRDS[part_key]
        a = span.start if idx == 0 else AstroDate._from_total_us(
            start_us + total * idx // 3)
        b = span.end if idx == 2 else AstroDate._from_total_us(
            start_us + total * (idx + 1) // 3)
        return DateSpan(a, b, basis=basis)
    if part_key in _HALVES:
        idx = _HALVES[part_key]
        if idx == 0:
            return DateSpan(span.start,
                            AstroDate._from_total_us(start_us + total // 2),
                            basis=basis)
        return DateSpan(AstroDate._from_total_us(start_us + total // 2),
                        span.end, basis=basis)
    raise ValueError(
        f"unknown subdivision {part!r}; expected one of "
        f"early/mid/late or first-half/second-half")


def subdivide(target: Union[NamedPeriod, DateSpan], part: str) -> DateSpan:
    """Return the early/mid/late (or first-/second-half) part of ``target``.

    ``target`` is a :class:`DateSpan` or a :class:`NamedPeriod`. For a bare
    span the result is the conventional arithmetic slice — thirds for
    early/mid/late, halves for first-/second-half.

    **Precedence.** When ``target`` is a :class:`NamedPeriod` and the registry
    holds an authority-defined subdivision for that part (an ICS epoch named
    "Early/Middle/Late <period>" whose parent is this entry), that chart span
    wins over arithmetic: ``subdivide(PERIODS["jurassic"], "late")`` returns
    the **Late Jurassic** span (161.5→143.1 Ma), *not* the last third of the
    Jurassic. Basis propagates through :func:`combine_basis` (parent ∘ child).
    """
    if isinstance(target, NamedPeriod):
        word = _CHART_WORD.get(part.strip().lower())
        if word is not None:
            wanted = _norm(f"{word} {target.name}")
            for child in children(target.key):
                if _norm(child.name) == wanted:
                    return DateSpan(
                        child.span.start, child.span.end,
                        basis=combine_basis(target.span.basis,
                                            child.span.basis))
        return _arithmetic_subdivide(target.span, part)
    if isinstance(target, DateSpan):
        return _arithmetic_subdivide(target, part)
    raise TypeError("subdivide target must be a NamedPeriod or DateSpan")


# --------------------------------------------------------------------------
# Radiocarbon calibration (coarse IntCal20)
# --------------------------------------------------------------------------
def _load_intcal() -> List[Tuple[int, float, float]]:
    out = []
    for line in _load_lines("intcal20_coarse.tab"):
        parts = line.split("\t")
        if parts[0] == "cal_bp":
            continue
        out.append((int(parts[0]), float(parts[1]), float(parts[2])))
    return out


#: The coarse IntCal20 samples: ``(cal_bp, c14_bp, sigma_14c)`` on a 100-yr grid.
INTCAL20_COARSE = _load_intcal()

_C14_MIN = min(r[1] for r in INTCAL20_COARSE)
_C14_MAX = max(r[1] for r in INTCAL20_COARSE)


def calibrate_c14(bp14c: Union[int, float]) -> DateSpan:
    """Coarsely calibrate a conventional radiocarbon age to a cal-BP span.

    ¹⁴C BP and cal BP are distinct reckonings; IntCal20 is the tabulated bridge.
    Given a conventional radiocarbon age ``bp14c`` (¹⁴C yr BP), this finds the
    nearest coarse sample of the curve and returns the calendar-BP interval
    where the curve's mean ¹⁴C age lies within one curve-σ of ``bp14c``, placed
    on the AD-1950 axis as a :class:`DateSpan` with ``basis="reconstructed"``.

    **This is demonstrative, not OxCal.** The curve is decimated to every 100th
    year and the lookup is a nearest-mean crossing, with no measurement-error
    propagation and no Bayesian highest-posterior-density intervals. Use it to
    locate a ¹⁴C age on the calendar axis, never for real radiocarbon dating.

    :raises ValueError: ``bp14c`` is outside the curve's ¹⁴C-age range.
    """
    if not _C14_MIN <= bp14c <= _C14_MAX:
        raise ValueError(
            f"{bp14c} 14C yr BP is outside the coarse IntCal20 range "
            f"[{_C14_MIN:.0f}, {_C14_MAX:.0f}]")
    nearest = min(INTCAL20_COARSE, key=lambda r: abs(r[1] - bp14c))
    sigma = nearest[2]
    matched = [cal for cal, c14, _ in INTCAL20_COARSE
               if abs(c14 - bp14c) <= sigma] or [nearest[0]]
    cal_hi, cal_lo = max(matched), min(matched)
    if cal_hi == cal_lo:  # single grid point -> ±one sample step
        cal_hi += 100
    return DateSpan(AstroDate(_BP_EPOCH_YEAR - cal_hi, 1, 1),
                    AstroDate(_BP_EPOCH_YEAR - cal_lo, 1, 1),
                    basis=BASIS_RECONSTRUCTED)
