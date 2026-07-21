"""``python -m chronologia`` — a small command-line front door.

Subcommands (each prints one friendly line to stdout)::

    chronologia convert 2024-06-01 --from gregorian --to hebrew
    chronologia extract "last summer" --lang en-us
    chronologia holidays US 2024 [--subdiv CA]
    chronologia easter 2024
    chronologia when 1984-06?

The heavy lifting lives in the library; this module only parses arguments and
formats results.  :func:`main` returns a process exit code (``0`` on success,
``2`` on a usage/lookup error) and is also the ``chronologia`` console-script
entry point.
"""
from __future__ import annotations

import argparse
from typing import List, Optional

import chronologia as c


def _parse_ymd(text: str) -> tuple:
    """Parse ``[-]Y-M-D`` into ``(year, month, day)`` ints (year may be < 0)."""
    neg = text.startswith("-")
    body = text[1:] if neg else text
    parts = body.split("-")
    if len(parts) != 3:
        raise ValueError(f"expected a Y-M-D date, got {text!r}")
    y, m, d = (int(p) for p in parts)
    return (-y if neg else y, m, d)


def _to_astro(cal: str, y: int, m: int, d: int) -> "c.AstroDate":
    if cal == "gregorian":
        return c.AstroDate(y, m, d)
    if cal not in c.CALENDARS:
        raise KeyError(cal)
    return c.AstroDate.from_calendar(cal, y, m, d)


def _cmd_convert(args: argparse.Namespace) -> int:
    y, m, d = _parse_ymd(args.date)
    try:
        astro = _to_astro(args.from_cal, y, m, d)
    except KeyError:
        print(f"unknown source calendar {args.from_cal!r}; known: "
              f"gregorian, {', '.join(sorted(c.CALENDARS))}")
        return 2
    if args.to_cal == "gregorian":
        out = f"gregorian {astro.year}-{astro.month:02d}-{astro.day:02d}"
    elif args.to_cal in c.CALENDARS:
        out = str(astro.to_calendar(args.to_cal))
    else:
        print(f"unknown target calendar {args.to_cal!r}; known: "
              f"gregorian, {', '.join(sorted(c.CALENDARS))}")
        return 2
    print(f"{args.from_cal} {args.date} = {out}")
    return 0


def _cmd_extract(args: argparse.Namespace) -> int:
    result = c.extract_timespan(args.text, lang=args.lang)
    if result is None:
        print(f"no date found in {args.text!r}")
        return 0
    span, matched = result
    print(f"{args.text!r} -> [{span.start.isoformat()}, "
          f"{span.end.isoformat()}) ({span.resolution.name.lower()})")
    return 0


def _cmd_holidays(args: argparse.Namespace) -> int:
    try:
        hols = c.holidays_for(args.jurisdiction, args.year, args.subdiv)
    except (KeyError, FileNotFoundError):
        print(f"no holiday data for jurisdiction {args.jurisdiction!r}")
        return 2
    if not hols:
        print(f"no holidays for {args.jurisdiction} {args.year}")
        return 0
    for h in hols:
        d = h.date
        print(f"{d.year:04d}-{d.month:02d}-{d.day:02d}  {h.name}")
    return 0


def _cmd_easter(args: argparse.Namespace) -> int:
    e = c.easter(args.year, args.method)
    print(f"Easter {args.year} ({args.method}): "
          f"{e.year:04d}-{e.month:02d}-{e.day:02d}")
    return 0


def _cmd_when(args: argparse.Namespace) -> int:
    try:
        edtf = c.parse_edtf(args.edtf)
    except Exception as exc:                        # EdtfParseError et al.
        print(f"could not parse EDTF {args.edtf!r}: {exc}")
        return 2
    span = edtf.span
    qual = f" [{edtf.qualifier}]" if edtf.qualifier else ""
    print(f"{args.edtf} -> [{span.start.isoformat()}, "
          f"{span.end.isoformat()}){qual}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chronologia",
        description="Calendrical and chronological command-line tools.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_conv = sub.add_parser("convert", help="convert a date between calendars")
    p_conv.add_argument("date", help="a Y-M-D date in the source calendar")
    p_conv.add_argument("--from", dest="from_cal", default="gregorian",
                        help="source calendar (default: gregorian)")
    p_conv.add_argument("--to", dest="to_cal", required=True,
                        help="target calendar")
    p_conv.set_defaults(func=_cmd_convert)

    p_ext = sub.add_parser("extract", help="extract a date span from text")
    p_ext.add_argument("text", help="the natural-language phrase")
    p_ext.add_argument("--lang", default="en-us", help="language (default en-us)")
    p_ext.set_defaults(func=_cmd_extract)

    p_hol = sub.add_parser("holidays", help="list civil holidays for a year")
    p_hol.add_argument("jurisdiction", help="jurisdiction code, e.g. US, PT")
    p_hol.add_argument("year", type=int)
    p_hol.add_argument("--subdiv", default=None,
                       help="subdivision code (e.g. a US state)")
    p_hol.set_defaults(func=_cmd_holidays)

    p_east = sub.add_parser("easter", help="compute Easter Sunday")
    p_east.add_argument("year", type=int)
    p_east.add_argument("--method", default="gregorian",
                        help="computus method (default gregorian)")
    p_east.set_defaults(func=_cmd_easter)

    p_when = sub.add_parser("when", help="resolve an EDTF string to a span")
    p_when.add_argument("edtf", help="an EDTF date string, e.g. 1984-06?")
    p_when.set_defaults(func=_cmd_when)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Parse ``argv`` and run the chosen subcommand; return an exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
