# Copyright 2018 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from pathlib import Path
import re
from typing import Callable, Dict, Union

from hscommon.build import read_changelog_file, filereplace
from sphinx.cmd.build import build_main as sphinx_build

CHANGELOG_FORMAT = """
{version} ({date})
----------------------

{description}
"""


def tixgen(tixurl: str) -> Callable[[str], str]:
    """This is a filter *generator*. tixurl is a url pattern for the tix with a {0} placeholder
    for the tix #
    """
    urlpattern = tixurl.format("\\1")  # will be replaced buy the content of the first group in re
    R = re.compile(r"#(\d+)")
    repl = f"`#\\1 <{urlpattern}>`__"
    return lambda text: R.sub(repl, text)


def gen(
    basepath: Path,
    destpath: Path,
    changelogpath: Path,
    tixurl: str,
    confrepl: Union[Dict[str, str], None] = None,
    confpath: Union[Path, None] = None,
    changelogtmpl: Union[Path, None] = None,
) -> None:
    """Generate sphinx docs with all bells and whistles.

    basepath: The base sphinx source path.
    destpath: The final path of html files
    changelogpath: The path to the changelog file to insert in changelog.rst.
    tixurl: The URL (with one formattable argument for the tix number) to the ticket system.
    confrepl: Dictionary containing replacements that have to be made in conf.py. {name: replacement}
    """
    if confrepl is None:
        confrepl = {}
    if confpath is None:
        confpath = Path(basepath, "conf.tmpl")
    if changelogtmpl is None:
        changelogtmpl = Path(basepath, "changelog.tmpl")
    changelog = read_changelog_file(changelogpath)
    tix = tixgen(tixurl)
    rendered_logs = []
    for log in changelog:
        description = tix(log["description"])
        # The format of the changelog descriptions is in markdown, but since we only use bulled list
        # and links, it's not worth depending on the markdown package. A simple regexp suffice.
        description = re.sub(r"\[(.*?)\]\((.*?)\)", "`\\1 <\\2>`__", description)
        rendered = CHANGELOG_FORMAT.format(version=log["version"], date=log["date_str"], description=description)
        rendered_logs.append(rendered)
    confrepl["version"] = changelog[0]["version"]
    changelog_out = Path(basepath, "changelog.rst")
    filereplace(changelogtmpl, changelog_out, changelog="\n".join(rendered_logs))
    if Path(confpath).exists():
        conf_out = Path(basepath, "conf.py")
        filereplace(confpath, conf_out, **confrepl)
    # Call the sphinx_build function, which is the same as doing sphinx-build from cli
    try:
        sphinx_build([str(basepath), str(destpath)])
    except SystemExit:
        print("Sphinx called sys.exit(), but we're cancelling it because we don't actually want to exit")
