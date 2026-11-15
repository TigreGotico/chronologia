# -*- coding: utf-8 -*-
"""The article before "próximo" or "último" belongs to the date.

"na próxima semana" is "em" with the article "a" (Priberam s.v. "em", 2:
"Usa-se para indicar tempo (ex.: em Janeiro; na próxima semana)"; s.v. "na":
"Contracção da preposição em e artigo ou pronome a").  Without the
preposition the article stays: "a próxima semana", "o próximo sábado".  It
opens the date, so it does not stay in the remainder.

Anchor Tuesday 2017-06-27.  The weeks start on Monday, so the next week is
2017-07-03 to 2017-07-10 and the last one 2017-06-19 to 2017-06-26.  The
next month is July 2017, the last year 2016.  The next Monday is 2017-07-03,
the next Saturday 2017-07-01, the last Friday 2017-06-23 and the last Sunday
2017-06-25.  Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from ._corpus import ad, nomatch, parse


@pytest.mark.parametrize("text,begin,end,rest", [
    ("a próxima semana", (2017, 7, 3), (2017, 7, 10), ""),
    ("a última semana", (2017, 6, 19), (2017, 6, 26), ""),
    ("o próximo mês", (2017, 7, 1), (2017, 8, 1), ""),
    ("o último ano", (2016, 1, 1), (2017, 1, 1), ""),
    ("a próxima segunda-feira", (2017, 7, 3), (2017, 7, 4), ""),
    ("o próximo sábado", (2017, 7, 1), (2017, 7, 2), ""),
    ("a última sexta-feira", (2017, 6, 23), (2017, 6, 24), ""),
    ("o último domingo", (2017, 6, 25), (2017, 6, 26), ""),
    ("vou à praia a próxima semana", (2017, 7, 3), (2017, 7, 10),
     "vou à praia"),
    ("na próxima semana", (2017, 7, 3), (2017, 7, 10), ""),
    ("próxima semana", (2017, 7, 3), (2017, 7, 10), ""),
    ("próximo sábado", (2017, 7, 1), (2017, 7, 2), ""),
])
def test_article_before_next_or_last(text, begin, end, rest):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(datetime(*begin)),
                                          ad(datetime(*end)))
    assert r.remainder == rest


@pytest.mark.parametrize("text", [
    "o próximo passo é simples",
    "a próxima pergunta é difícil",
    "a última vez que o vi",
    "o último a sair apaga a luz",
])
def test_article_before_next_or_last_without_a_date(text):
    nomatch(text)


# A plural article before "próximos" or "últimos" opens a stretch of several
# units: "nos próximos dias" is "in the coming days", "nos últimos anos" is
# "in recent years".  Neither phrase names one day or one year.  The article
# is not folded, so the phrase refuses or keeps its article in the remainder.
@pytest.mark.parametrize("text,article", [
    ("nos próximos dias", "nos"),
    ("os próximos meses", "os"),
    ("as próximas semanas", "as"),
    ("nas próximas semanas", "nas"),
    ("nos últimos anos", "nos"),
    ("nos últimos meses", "nos"),
    ("as últimas semanas", "as"),
    ("as últimas sextas-feiras", "as"),
    ("os próximos sábados", "os"),
])
def test_plural_article_is_not_folded(text, article):
    r = parse(text)
    assert r is None or article in r.remainder.split(), (
        f"{text!r} read {r!r}: the plural article was folded")
