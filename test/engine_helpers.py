"""Shared fixtures for the declarative-engine unit tests."""
import os
from datetime import datetime

from chronologia.extract import DateTimeEngine, load_lang_spec

LOCALE_DIR = os.path.join(os.path.dirname(__file__), "engine_locale")

#: fixed anchor used across every resolver assertion (a Tuesday, 13:04)
ANCHOR = datetime(2017, 6, 27, 13, 4)


def load_zz():
    return load_lang_spec("zz", LOCALE_DIR)


def zz_engine():
    return DateTimeEngine(load_zz())
