import os
import os.path as op
import shutil
import tempfile
from typing import Any, List

import polib

from hscommon import pygettext

LC_MESSAGES = "LC_MESSAGES"


def get_langs(folder: str) -> List[str]:
    return [name for name in os.listdir(folder) if op.isdir(op.join(folder, name))]


def files_with_ext(folder: str, ext: str) -> List[str]:
    return [op.join(folder, fn) for fn in os.listdir(folder) if fn.endswith(ext)]


def generate_pot(folders: List[str], outpath: str, keywords: Any, merge: bool = False) -> None:
    if merge and not op.exists(outpath):
        merge = False
    if merge:
        _, genpath = tempfile.mkstemp()
    else:
        genpath = outpath
    pyfiles = []
    for folder in folders:
        for root, dirs, filenames in os.walk(folder):
            keep = [fn for fn in filenames if fn.endswith(".py")]
            pyfiles += [op.join(root, fn) for fn in keep]
    pygettext.main(pyfiles, outpath=genpath, keywords=keywords)
    if merge:
        merge_po_and_preserve(genpath, outpath)
        try:
            os.remove(genpath)
        except Exception:
            print("Exception while removing temporary folder %s\n", genpath)


def compile_all_po(base_folder: str) -> None:
    langs = get_langs(base_folder)
    for lang in langs:
        pofolder = op.join(base_folder, lang, LC_MESSAGES)
        pofiles = files_with_ext(pofolder, ".po")
        for pofile in pofiles:
            p = polib.pofile(pofile)
            p.save_as_mofile(pofile[:-3] + ".mo")


def merge_locale_dir(target: str, mergeinto: str) -> None:
    langs = get_langs(target)
    for lang in langs:
        if not op.exists(op.join(mergeinto, lang)):
            continue
        mofolder = op.join(target, lang, LC_MESSAGES)
        mofiles = files_with_ext(mofolder, ".mo")
        for mofile in mofiles:
            shutil.copy(mofile, op.join(mergeinto, lang, LC_MESSAGES))


def merge_pots_into_pos(folder: str) -> None:
    # We're going to take all pot files in `folder` and for each lang, merge it with the po file
    # with the same name.
    potfiles = files_with_ext(folder, ".pot")
    for potfile in potfiles:
        refpot = polib.pofile(potfile)
        refname = op.splitext(op.basename(potfile))[0]
        for lang in get_langs(folder):
            po = polib.pofile(op.join(folder, lang, LC_MESSAGES, refname + ".po"))
            po.merge(refpot)
            po.save()


def merge_po_and_preserve(source: str, dest: str) -> None:
    # Merges source entries into dest, but keep old entries intact
    sourcepo = polib.pofile(source)
    destpo = polib.pofile(dest)
    for entry in sourcepo:
        if destpo.find(entry.msgid) is not None:
            # The entry is already there
            continue
        destpo.append(entry)
    destpo.save()


def normalize_all_pos(base_folder: str) -> None:
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
        pofiles = files_with_ext(pofolder, ".po")
        for pofile in pofiles:
            p = polib.pofile(pofile)
            p.save()
