import os
import os.path as op
import shutil
import re
import tempfile

import polib

from . import pygettext
from .util import modified_after, dedupe, ensure_folder, ensure_file
from .build import print_and_do, ensure_empty_folder, copy

LC_MESSAGES = 'LC_MESSAGES'

def get_langs(folder):
    return [name for name in os.listdir(folder) if op.isdir(op.join(folder, name))]

def files_with_ext(folder, ext):
    return [op.join(folder, fn) for fn in os.listdir(folder) if fn.endswith(ext)]

def generate_pot(folders, outpath, keywords, merge=False):
    if merge and not op.exists(outpath):
        merge = False
    if merge:
        _, genpath = tempfile.mkstemp()
    else:
        genpath = outpath
    pyfiles = []
    for folder in folders:
        for root, dirs, filenames in os.walk(folder):
            keep = [fn for fn in filenames if fn.endswith('.py')]
            pyfiles += [op.join(root, fn) for fn in keep]
    pygettext.main(pyfiles, outpath=genpath, keywords=keywords)
    if merge:
        merge_po_and_preserve(genpath, outpath)
        os.remove(genpath)

def compile_all_po(base_folder):
    langs = get_langs(base_folder)
    for lang in langs:
        pofolder = op.join(base_folder, lang, LC_MESSAGES)
        pofiles = files_with_ext(pofolder, '.po')
        for pofile in pofiles:
            p = polib.pofile(pofile)
            p.save_as_mofile(pofile[:-3] + '.mo')

def merge_locale_dir(target, mergeinto):
    langs = get_langs(target)
    for lang in langs:
        if not op.exists(op.join(mergeinto, lang)):
            continue
        mofolder = op.join(target, lang, LC_MESSAGES)
        mofiles = files_with_ext(mofolder, '.mo')
        for mofile in mofiles:
            shutil.copy(mofile, op.join(mergeinto, lang, LC_MESSAGES))

def merge_pots_into_pos(folder):
    # We're going to take all pot files in `folder` and for each lang, merge it with the po file
    # with the same name.
    potfiles = files_with_ext(folder, '.pot')
    for potfile in potfiles:
        refpot = polib.pofile(potfile)
        refname = op.splitext(op.basename(potfile))[0]
        for lang in get_langs(folder):
            po = polib.pofile(op.join(folder, lang, LC_MESSAGES, refname + '.po'))
            po.merge(refpot)
            po.save()

def merge_po_and_preserve(source, dest):
    # Merges source entries into dest, but keep old entries intact
    sourcepo = polib.pofile(source)
    destpo = polib.pofile(dest)
    for entry in sourcepo:
        if destpo.find(entry.msgid) is not None:
            # The entry is already there
            continue
        destpo.append(entry)
    destpo.save()

def normalize_all_pos(base_folder):
    """Normalize the format of .po files in base_folder.
    
    When getting POs from external sources, such as Transifex, we end up with spurious diffs because
    of a difference in the way line wrapping is handled. It wouldn't be a big deal if it happened
    once, but these spurious diffs keep overwriting each other, and it's annoying.
    
    Our PO files will keep polib's format. Call this function to ensure that freshly pulled POs
    are of the right format before committing them.
    """
    langs = get_langs(base_folder)
    for lang in langs:
        pofolder = op.join(base_folder, lang, LC_MESSAGES)
        pofiles = files_with_ext(pofolder, '.po')
        for pofile in pofiles:
            p = polib.pofile(pofile)
            p.save()

#--- Cocoa
def all_lproj_paths(folder):
    return files_with_ext(folder, '.lproj')

def escape_cocoa_strings(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def unescape_cocoa_strings(s):
    return s.replace('\\\\', '\\').replace('\\"', '"').replace('\\n', '\n')

def strings2pot(target, dest):
    with open(target, 'rt', encoding='utf-8') as fp:
        contents = fp.read()
    # We're reading an en.lproj file. We only care about the righthand part of the translation.
    re_trans = re.compile(r'".*" = "(.*)";')
    strings = re_trans.findall(contents)
    if op.exists(dest):
        po = polib.pofile(dest)
    else:
        po = polib.POFile()
    for s in dedupe(strings):
        s = unescape_cocoa_strings(s)
        entry = po.find(s)
        if entry is None:
            entry = polib.POEntry(msgid=s)
            po.append(entry)
        # we don't know or care about a line number so we put 0
        entry.occurrences.append((target, '0'))
        entry.occurrences = dedupe(entry.occurrences)
    po.save(dest)

def allstrings2pot(lprojpath, dest, excludes=None):
    allstrings = files_with_ext(lprojpath, '.strings')
    if excludes:
        allstrings = [p for p in allstrings if op.splitext(op.basename(p))[0] not in excludes]
    for strings_path in allstrings:
        strings2pot(strings_path, dest)

def po2strings(pofile, en_strings, dest):
    # Takes en_strings and replace all righthand parts of "foo" = "bar"; entries with translations
    # in pofile, then puts the result in dest.
    po = polib.pofile(pofile)
    if not modified_after(pofile, dest):
        return
    ensure_folder(op.dirname(dest))
    print("Creating {} from {}".format(dest, pofile))
    with open(en_strings, 'rt', encoding='utf-8') as fp:
        contents = fp.read()
    re_trans = re.compile(r'(?<= = ").*(?=";\n)')
    def repl(match):
        s = match.group(0)
        unescaped = unescape_cocoa_strings(s)
        entry = po.find(unescaped)
        if entry is None:
            print("WARNING: Could not find entry '{}' in .po file".format(s))
            return s
        trans = entry.msgstr
        return escape_cocoa_strings(trans) if trans else s
    contents = re_trans.sub(repl, contents)
    with open(dest, 'wt', encoding='utf-8') as fp:
        fp.write(contents)

def generate_cocoa_strings_from_code(code_folder, dest_folder):
    # Uses the "genstrings" command to generate strings file from all .m files in "code_folder".
    # The strings file (their name depends on the localization table used in the source) will be
    # placed in "dest_folder".
    # genstrings produces utf-16 files with comments. After having generated the files, we convert
    # them to utf-8 and remove the comments.
    ensure_empty_folder(dest_folder)
    print_and_do('genstrings -o "{}" `find "{}" -name *.m | xargs`'.format(dest_folder, code_folder))
    for stringsfile in os.listdir(dest_folder):
        stringspath = op.join(dest_folder, stringsfile)
        with open(stringspath, 'rt', encoding='utf-16') as fp:
            content = fp.read()
        content = re.sub('/\*.*?\*/', '', content)
        content = re.sub('\n{2,}', '\n', content)
        # I have no idea why, but genstrings seems to have problems with "%" character in strings
        # and inserts (number)$ after it. Find these bogus inserts and remove them.
        content = re.sub('%\d\$', '%', content)
        with open(stringspath, 'wt', encoding='utf-8') as fp:
            fp.write(content)

def build_cocoa_localizations(app, en_stringsfile=op.join('cocoa', 'en.lproj', 'Localizable.strings')):
    # Creates .lproj folders with Localizable.strings and cocoalib.strings based on cocoalib.po and
    # ui.po for all available languages as well as base strings files in en.lproj. These lproj
    # folders are created in `app`'s (a OSXAppStructure) resource folder.
    print("Creating lproj folders based on .po files")
    en_cocoastringsfile = op.join('cocoalib', 'en.lproj', 'cocoalib.strings')
    for lang in get_langs('locale'):
        pofile = op.join('locale', lang, 'LC_MESSAGES', 'ui.po')
        dest_lproj = op.join(app.resources, lang + '.lproj')
        ensure_folder(dest_lproj)
        po2strings(pofile, en_stringsfile, op.join(dest_lproj, 'Localizable.strings'))
        pofile = op.join('cocoalib', 'locale', lang, 'LC_MESSAGES', 'cocoalib.po')
        po2strings(pofile, en_cocoastringsfile, op.join(dest_lproj, 'cocoalib.strings'))
    # We also have to copy the "en.lproj" strings
    en_lproj = op.join(app.resources, 'en.lproj')
    ensure_folder(en_lproj)
    copy(en_stringsfile, en_lproj)
    copy(en_cocoastringsfile, en_lproj)
