# Created By: Virgil Dupras
# Created On: 2010-06-23
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# Doing i18n with GNU gettext for the core text gets complicated, so what I do is that I make the
# GUI layer responsible for supplying a tr() function.

import os
from typing import Callable, Union

from hscommon.plat import ISLINUX

_trfunc = None
_trget = None
installed_lang = None


def tr(s: str, context: Union[str, None] = None) -> str:
    if _trfunc is None:
        return s
    else:
        if context:
            return _trfunc(s, context)
        else:
            return _trfunc(s)


def trget(domain: str) -> Callable[[str], str]:
    # Returns a tr() function for the specified domain.
    if _trget is None:
        return lambda s: tr(s, domain)
    else:
        return _trget(domain)


def set_tr(
    new_tr: Callable[[str, Union[str, None]], str],
    new_trget: Union[Callable[[str], Callable[[str], str]], None] = None,
) -> None:
    global _trfunc, _trget
    _trfunc = new_tr
    if new_trget is not None:
        _trget = new_trget


def get_locale_name(lang: str) -> Union[str, None]:
    # Removed old conversion code as windows seems to support these
    LANG2LOCALENAME = {
        "cs": "cs_CZ",
        "de": "de_DE",
        "el": "el_GR",
        "en": "en",
        "es": "es_ES",
        "fr": "fr_FR",
        "hy": "hy_AM",
        "it": "it_IT",
        "ja": "ja_JP",
        "ko": "ko_KR",
        "ms": "ms_MY",
        "nl": "nl_NL",
        "pl_PL": "pl_PL",
        "pt_BR": "pt_BR",
        "ru": "ru_RU",
        "tr": "tr_TR",
        "uk": "uk_UA",
        "vi": "vi_VN",
        "zh_CN": "zh_CN",
    }
    if lang not in LANG2LOCALENAME:
        return None
    result = LANG2LOCALENAME[lang]
    if ISLINUX:
        result += ".UTF-8"
    return result


# --- gettext
def install_gettext_trans(base_folder: os.PathLike, lang: str) -> None:
    import gettext

    def gettext_trget(domain: str) -> Callable[[str], str]:
        if not lang:
            return lambda s: s
        try:
            return gettext.translation(domain, localedir=base_folder, languages=[lang]).gettext
        except OSError:
            return lambda s: s

    default_gettext = gettext_trget("core")

    def gettext_tr(s: str, context: Union[str, None] = None) -> str:
        if not context:
            return default_gettext(s)
        else:
            trfunc = gettext_trget(context)
            return trfunc(s)

    set_tr(gettext_tr, gettext_trget)
    global installed_lang
    installed_lang = lang
