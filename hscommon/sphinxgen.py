# Created By: Virgil Dupras
# Created On: 2011-01-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os.path as op
import re

from pkg_resources import load_entry_point

from .build import read_changelog_file, filereplace

CHANGELOG_FORMAT = """
{version} ({date})
----------------------

{description}
"""

def tixgen(tixurl):
    """This is a filter *generator*. tixurl is a url pattern for the tix with a {0} placeholder
    for the tix #
    """
    urlpattern = tixurl.format('\\1') # will be replaced buy the content of the first group in re
    R = re.compile(r'#(\d+)')
    repl = '`#\\1 <{}>`__'.format(urlpattern)
    return lambda text: R.sub(repl, text)

def gen(basepath, destpath, changelogpath, tixurl, confrepl=None, confpath=None, changelogtmpl=None):
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
        confpath = op.join(basepath, 'conf.tmpl')
    if changelogtmpl is None:
        changelogtmpl = op.join(basepath, 'changelog.tmpl')
    changelog = read_changelog_file(changelogpath)
    tix = tixgen(tixurl)
    rendered_logs = []
    for log in changelog:
        description = tix(log['description'])
        # The format of the changelog descriptions is in markdown, but since we only use bulled list
        # and links, it's not worth depending on the markdown package. A simple regexp suffice.
        description = re.sub(r'\[(.*?)\]\((.*?)\)', '`\\1 <\\2>`__', description)
        rendered = CHANGELOG_FORMAT.format(version=log['version'], date=log['date_str'],
            description=description)
        rendered_logs.append(rendered)
    confrepl['version'] = changelog[0]['version']
    changelog_out = op.join(basepath, 'changelog.rst')
    filereplace(changelogtmpl, changelog_out, changelog='\n'.join(rendered_logs))
    conf_out = op.join(basepath, 'conf.py')
    filereplace(confpath, conf_out, **confrepl)
    # We used to call sphinx-build with print_and_do(), but the problem was that the virtualenv
    # of the calling python wasn't correctly considered and caused problems with documentation
    # relying on autodoc (which tries to import the module to auto-document, but fail because of
    # missing dependencies which are in the virtualenv). Here, we do exactly what is done when
    # calling the command from bash.
    cmd = load_entry_point('Sphinx', 'console_scripts', 'sphinx-build')
    try:
        cmd(['sphinx-build', basepath, destpath])
    except SystemExit:
        print("Sphinx called sys.exit(), but we're cancelling it because we don't actually want to exit")

