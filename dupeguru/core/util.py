# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import time
import sys
import os
import urllib.request
import urllib.error
import json
import semantic_version
import logging
from typing import Union

from hscommon.util import format_time_decimal


def format_timestamp(t, delta):
    if delta:
        return format_time_decimal(t)
    else:
        if t > 0:
            return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(t))
        else:
            return "---"


def format_words(w):
    def do_format(w):
        if isinstance(w, list):
            return "(%s)" % ", ".join(do_format(item) for item in w)
        else:
            return w.replace("\n", " ")

    return ", ".join(do_format(item) for item in w)


def format_perc(p):
    return "%0.0f" % p


def format_dupe_count(c):
    return str(c) if c else "---"


def cmp_value(dupe, attrname):
    value = getattr(dupe, attrname, "")
    return value.lower() if isinstance(value, str) else value


def fix_surrogate_encoding(s, encoding="utf-8"):
    # ref #210. It's possible to end up with file paths that, while correct unicode strings, are
    # decoded with the 'surrogateescape' option, which make the string unencodable to utf-8. We fix
    # these strings here by trying to encode them and, if it fails, we do an encode/decode dance
    # to remove the problematic characters. This dance is *lossy* but there's not much we can do
    # because if we end up with this type of string, it means that we don't know the encoding of the
    # underlying filesystem that brought them. Don't use this for strings you're going to re-use in
    # fs-related functions because you're going to lose your path (it's going to change). Use this
    # if you need to export the path somewhere else, outside of the unicode realm.
    # See http://lucumr.pocoo.org/2013/7/2/the-updated-guide-to-unicode/
    try:
        s.encode(encoding)
    except UnicodeEncodeError:
        return s.encode(encoding, "replace").decode(encoding)
    else:
        return s


def executable_folder():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def check_for_update(current_version: str, include_prerelease: bool = False) -> Union[None, dict]:
    request = urllib.request.Request(
        "https://api.github.com/repos/arsenetar/dupeguru/releases",
        headers={"Accept": "application/vnd.github.v3+json"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            if response.status != 200:
                logging.warn(f"Error retriving updates. Status: {response.status}")
                return None
            try:
                response_json = json.loads(response.read())
            except json.JSONDecodeError as ex:
                logging.warn(f"Error parsing updates. {ex.msg}")
                return None
    except urllib.error.URLError as ex:
        logging.warn(f"Error retriving updates. {ex.reason}")
        return None
    new_version = semantic_version.Version(current_version)
    new_url = None
    for release in response_json:
        release_version = semantic_version.Version(release["name"])
        if new_version < release_version and (include_prerelease or not release_version.prerelease):
            new_version = release_version
            new_url = release["html_url"]
    if new_url is not None:
        return {"version": new_version, "url": new_url}
    else:
        return None
