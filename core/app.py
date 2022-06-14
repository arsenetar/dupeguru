# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import cProfile
import datetime
import os
import os.path as op
import logging
import subprocess
import re
import shutil
from pathlib import Path

from send2trash import send2trash
from hscommon.jobprogress import job
from hscommon.notify import Broadcaster
from hscommon.conflict import smart_move, smart_copy
from hscommon.gui.progress_window import ProgressWindow
from hscommon.util import delete_if_empty, first, escape, nonone, allsame
from hscommon.trans import tr
from hscommon import desktop

from core import se, me, pe
from core.pe.photo import get_delta_dimensions
from core.util import cmp_value, fix_surrogate_encoding
from core import directories, results, export, fs, prioritize
from core.ignore import IgnoreList
from core.exclude import ExcludeDict as ExcludeList
from core.scanner import ScanType
from core.gui.deletion_options import DeletionOptions
from core.gui.details_panel import DetailsPanel
from core.gui.directory_tree import DirectoryTree
from core.gui.ignore_list_dialog import IgnoreListDialog
from core.gui.exclude_list_dialog import ExcludeListDialogCore
from core.gui.problem_dialog import ProblemDialog
from core.gui.stats_label import StatsLabel

HAD_FIRST_LAUNCH_PREFERENCE = "HadFirstLaunch"
DEBUG_MODE_PREFERENCE = "DebugMode"

MSG_NO_MARKED_DUPES = tr("There are no marked duplicates. Nothing has been done.")
MSG_NO_SELECTED_DUPES = tr("There are no selected duplicates. Nothing has been done.")
MSG_MANY_FILES_TO_OPEN = tr(
    "You're about to open many files at once. Depending on what those "
    "files are opened with, doing so can create quite a mess. Continue?"
)


class DestType:
    DIRECT = 0
    RELATIVE = 1
    ABSOLUTE = 2


class JobType:
    SCAN = "job_scan"
    LOAD = "job_load"
    MOVE = "job_move"
    COPY = "job_copy"
    DELETE = "job_delete"


class AppMode:
    STANDARD = 0
    MUSIC = 1
    PICTURE = 2


JOBID2TITLE = {
    JobType.SCAN: tr("Scanning for duplicates"),
    JobType.LOAD: tr("Loading"),
    JobType.MOVE: tr("Moving"),
    JobType.COPY: tr("Copying"),
    JobType.DELETE: tr("Sending to Trash"),
}


class DupeGuru(Broadcaster):
    """Holds everything together.

    Instantiated once per running application, it holds a reference to every high-level object
    whose reference needs to be held: :class:`~core.results.Results`,
    :class:`~core.directories.Directories`, :mod:`core.gui` instances, etc..

    It also hosts high level methods and acts as a coordinator for all those elements. This is why
    some of its methods seem a bit shallow, like for example :meth:`mark_all` and
    :meth:`remove_duplicates`. These methos are just proxies for a method in :attr:`results`, but
    they are also followed by a notification call which is very important if we want GUI elements
    to be correctly notified of a change in the data they're presenting.

    .. attribute:: directories

        Instance of :class:`~core.directories.Directories`. It holds the current folder selection.

    .. attribute:: results

        Instance of :class:`core.results.Results`. Holds the results of the latest scan.

    .. attribute:: selected_dupes

        List of currently selected dupes from our :attr:`results`. Whenever the user changes its
        selection at the UI level, :attr:`result_table` takes care of updating this attribute, so
        you can trust that it's always up-to-date.

    .. attribute:: result_table

        Instance of :mod:`meta-gui <core.gui>` table listing the results from :attr:`results`
    """

    # --- View interface
    # get_default(key_name)
    # set_default(key_name, value)
    # show_message(msg)
    # open_url(url)
    # open_path(path)
    # reveal_path(path)
    # ask_yes_no(prompt) --> bool
    # create_results_window()
    # show_results_window()
    # show_problem_dialog()
    # select_dest_folder(prompt: str) --> str
    # select_dest_file(prompt: str, ext: str) --> str

    NAME = PROMPT_NAME = "dupeGuru"

    PICTURE_CACHE_TYPE = "sqlite"  # set to 'shelve' for a ShelveCache

    def __init__(self, view, portable=False):
        if view.get_default(DEBUG_MODE_PREFERENCE):
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug("Debug mode enabled")
        Broadcaster.__init__(self)
        self.view = view
        self.appdata = desktop.special_folder_path(desktop.SpecialFolder.APPDATA, portable=portable)
        if not op.exists(self.appdata):
            os.makedirs(self.appdata)
        self.app_mode = AppMode.STANDARD
        self.discarded_file_count = 0
        self.exclude_list = ExcludeList()
        hash_cache_file = op.join(self.appdata, "hash_cache.db")
        fs.filesdb.connect(hash_cache_file)
        self.directories = directories.Directories(self.exclude_list)
        self.results = results.Results(self)
        self.ignore_list = IgnoreList()
        # In addition to "app-level" options, this dictionary also holds options that will be
        # sent to the scanner. They don't have default values because those defaults values are
        # defined in the scanner class.
        self.options = {
            "escape_filter_regexp": True,
            "clean_empty_dirs": False,
            "ignore_hardlink_matches": False,
            "copymove_dest_type": DestType.RELATIVE,
            "picture_cache_type": self.PICTURE_CACHE_TYPE,
        }
        self.selected_dupes = []
        self.details_panel = DetailsPanel(self)
        self.directory_tree = DirectoryTree(self)
        self.problem_dialog = ProblemDialog(self)
        self.ignore_list_dialog = IgnoreListDialog(self)
        self.exclude_list_dialog = ExcludeListDialogCore(self)
        self.stats_label = StatsLabel(self)
        self.result_table = None
        self.deletion_options = DeletionOptions()
        self.progress_window = ProgressWindow(self._job_completed, self._job_error)
        children = [self.directory_tree, self.stats_label, self.details_panel]
        for child in children:
            child.connect()

    # --- Private
    def _recreate_result_table(self):
        if self.result_table is not None:
            self.result_table.disconnect()
        if self.app_mode == AppMode.PICTURE:
            self.result_table = pe.result_table.ResultTable(self)
        elif self.app_mode == AppMode.MUSIC:
            self.result_table = me.result_table.ResultTable(self)
        else:
            self.result_table = se.result_table.ResultTable(self)
        self.result_table.connect()
        self.view.create_results_window()

    def _get_picture_cache_path(self):
        cache_type = self.options["picture_cache_type"]
        cache_name = "cached_pictures.shelve" if cache_type == "shelve" else "cached_pictures.db"
        return op.join(self.appdata, cache_name)

    def _get_dupe_sort_key(self, dupe, get_group, key, delta):
        if self.app_mode in (AppMode.MUSIC, AppMode.PICTURE) and key == "folder_path":
            dupe_folder_path = getattr(dupe, "display_folder_path", dupe.folder_path)
            return str(dupe_folder_path).lower()
        if self.app_mode == AppMode.PICTURE and delta and key == "dimensions":
            r = cmp_value(dupe, key)
            ref_value = cmp_value(get_group().ref, key)
            return get_delta_dimensions(r, ref_value)
        if key == "marked":
            return self.results.is_marked(dupe)
        if key == "percentage":
            m = get_group().get_match_of(dupe)
            return m.percentage
        elif key == "dupe_count":
            return 0
        else:
            result = cmp_value(dupe, key)
        if delta:
            refval = cmp_value(get_group().ref, key)
            if key in self.result_table.DELTA_COLUMNS:
                result -= refval
            else:
                same = cmp_value(dupe, key) == refval
                result = (same, result)
        return result

    def _get_group_sort_key(self, group, key):
        if self.app_mode in (AppMode.MUSIC, AppMode.PICTURE) and key == "folder_path":
            dupe_folder_path = getattr(group.ref, "display_folder_path", group.ref.folder_path)
            return str(dupe_folder_path).lower()
        if key == "percentage":
            return group.percentage
        if key == "dupe_count":
            return len(group)
        if key == "marked":
            return len([dupe for dupe in group.dupes if self.results.is_marked(dupe)])
        return cmp_value(group.ref, key)

    def _do_delete(self, j, link_deleted, use_hardlinks, direct_deletion):
        def op(dupe):
            j.add_progress()
            return self._do_delete_dupe(dupe, link_deleted, use_hardlinks, direct_deletion)

        j.start_job(self.results.mark_count)
        self.results.perform_on_marked(op, True)

    def _do_delete_dupe(self, dupe, link_deleted, use_hardlinks, direct_deletion):
        if not dupe.path.exists():
            return
        logging.debug("Sending '%s' to trash", dupe.path)
        str_path = str(dupe.path)
        if direct_deletion:
            if op.isdir(str_path):
                shutil.rmtree(str_path)
            else:
                os.remove(str_path)
        else:
            send2trash(str_path)  # Raises OSError when there's a problem
        if link_deleted:
            group = self.results.get_group_of_duplicate(dupe)
            ref = group.ref
            linkfunc = os.link if use_hardlinks else os.symlink
            linkfunc(str(ref.path), str_path)
        self.clean_empty_dirs(dupe.path.parent)

    def _create_file(self, path):
        # We add fs.Folder to fileclasses in case the file we're loading contains folder paths.
        return fs.get_file(path, self.fileclasses + [se.fs.Folder])

    def _get_file(self, str_path):
        path = Path(str_path)
        f = self._create_file(path)
        if f is None:
            return None
        try:
            f._read_all_info(attrnames=self.METADATA_TO_READ)
            return f
        except OSError:
            return None

    def _get_export_data(self):
        columns = [col for col in self.result_table._columns.ordered_columns if col.visible and col.name != "marked"]
        colnames = [col.display for col in columns]
        rows = []
        for group_id, group in enumerate(self.results.groups):
            for dupe in group:
                data = self.get_display_info(dupe, group)
                row = [fix_surrogate_encoding(data[col.name]) for col in columns]
                row.insert(0, group_id)
                rows.append(row)
        return colnames, rows

    def _results_changed(self):
        self.selected_dupes = [d for d in self.selected_dupes if self.results.get_group_of_duplicate(d) is not None]
        self.notify("results_changed")

    def _start_job(self, jobid, func, args=()):
        title = JOBID2TITLE[jobid]
        try:
            self.progress_window.run(jobid, title, func, args=args)
        except job.JobInProgressError:
            msg = tr(
                "A previous action is still hanging in there. You can't start a new one yet. Wait "
                "a few seconds, then try again."
            )
            self.view.show_message(msg)

    def _job_completed(self, jobid):
        if jobid == JobType.SCAN:
            self._results_changed()
            fs.filesdb.commit()
            if not self.results.groups:
                self.view.show_message(tr("No duplicates found."))
            else:
                self.view.show_results_window()
        if jobid in {JobType.MOVE, JobType.DELETE}:
            self._results_changed()
        if jobid == JobType.LOAD:
            self._recreate_result_table()
            self._results_changed()
            self.view.show_results_window()
        if jobid in {JobType.COPY, JobType.MOVE, JobType.DELETE}:
            if self.results.problems:
                self.problem_dialog.refresh()
                self.view.show_problem_dialog()
            else:
                if jobid == JobType.COPY:
                    msg = tr("All marked files were copied successfully.")
                elif jobid == JobType.MOVE:
                    msg = tr("All marked files were moved successfully.")
                elif jobid == JobType.DELETE and self.deletion_options.direct:
                    msg = tr("All marked files were deleted successfully.")
                else:
                    msg = tr("All marked files were successfully sent to Trash.")
                self.view.show_message(msg)

    def _job_error(self, jobid, err):
        if jobid == JobType.LOAD:
            msg = tr("Could not load file: {}").format(err)
            self.view.show_message(msg)
            return False
        else:
            raise err

    @staticmethod
    def _remove_hardlink_dupes(files):
        seen_inodes = set()
        result = []
        for file in files:
            try:
                inode = file.path.stat().st_ino
            except OSError:
                # The file was probably deleted or something
                continue
            if inode not in seen_inodes:
                seen_inodes.add(inode)
                result.append(file)
        return result

    def _select_dupes(self, dupes):
        if dupes == self.selected_dupes:
            return
        self.selected_dupes = dupes
        self.notify("dupes_selected")

    # --- Protected
    def _get_fileclasses(self):
        if self.app_mode == AppMode.PICTURE:
            return [pe.photo.PLAT_SPECIFIC_PHOTO_CLASS]
        elif self.app_mode == AppMode.MUSIC:
            return [me.fs.MusicFile]
        else:
            return [se.fs.File]

    def _prioritization_categories(self):
        if self.app_mode == AppMode.PICTURE:
            return pe.prioritize.all_categories()
        elif self.app_mode == AppMode.MUSIC:
            return me.prioritize.all_categories()
        else:
            return prioritize.all_categories()

    # --- Public
    def add_directory(self, d):
        """Adds folder ``d`` to :attr:`directories`.

        Shows an error message dialog if something bad happens.

        :param str d: path of folder to add
        """
        try:
            self.directories.add_path(Path(d))
            self.notify("directories_changed")
        except directories.AlreadyThereError:
            self.view.show_message(tr("'{}' already is in the list.").format(d))
        except directories.InvalidPathError:
            self.view.show_message(tr("'{}' does not exist.").format(d))

    def add_selected_to_ignore_list(self):
        """Adds :attr:`selected_dupes` to :attr:`ignore_list`."""
        dupes = self.without_ref(self.selected_dupes)
        if not dupes:
            self.view.show_message(MSG_NO_SELECTED_DUPES)
            return
        msg = tr("All selected %d matches are going to be ignored in all subsequent scans. Continue?")
        if not self.view.ask_yes_no(msg % len(dupes)):
            return
        for dupe in dupes:
            g = self.results.get_group_of_duplicate(dupe)
            for other in g:
                if other is not dupe:
                    self.ignore_list.ignore(str(other.path), str(dupe.path))
        self.remove_duplicates(dupes)
        self.ignore_list_dialog.refresh()

    def apply_filter(self, result_filter):
        """Apply a filter ``filter`` to the results so that it shows only dupe groups that match it.

        :param str filter: filter to apply
        """
        self.results.apply_filter(None)
        if self.options["escape_filter_regexp"]:
            result_filter = escape(result_filter, set("()[]\\.|+?^"))
            result_filter = escape(result_filter, "*", ".")
        self.results.apply_filter(result_filter)
        self._results_changed()

    def clean_empty_dirs(self, path):
        if self.options["clean_empty_dirs"]:
            while delete_if_empty(path, [".DS_Store"]):
                path = path.parent

    def clear_picture_cache(self):
        try:
            os.remove(self._get_picture_cache_path())
        except FileNotFoundError:
            pass  # we don't care

    def clear_hash_cache(self):
        fs.filesdb.clear()

    def copy_or_move(self, dupe, copy: bool, destination: str, dest_type: DestType):
        source_path = dupe.path
        location_path = first(p for p in self.directories if p in dupe.path.parents)
        dest_path = Path(destination)
        if dest_type in {DestType.RELATIVE, DestType.ABSOLUTE}:
            # no filename, no windows drive letter
            source_base = source_path.relative_to(source_path.anchor).parent
            if dest_type == DestType.RELATIVE:
                source_base = source_base.relative_to(location_path.relative_to(location_path.anchor))
            dest_path = dest_path.joinpath(source_base)
        if not dest_path.exists():
            dest_path.mkdir(parents=True)
        # Add filename to dest_path. For file move/copy, it's not required, but for folders, yes.
        dest_path = dest_path.joinpath(source_path.name)
        logging.debug("Copy/Move operation from '%s' to '%s'", source_path, dest_path)
        # Raises an EnvironmentError if there's a problem
        if copy:
            smart_copy(source_path, dest_path)
        else:
            smart_move(source_path, dest_path)
            self.clean_empty_dirs(source_path.parent)

    def copy_or_move_marked(self, copy):
        """Start an async move (or copy) job on marked duplicates.

        :param bool copy: If True, duplicates will be copied instead of moved
        """

        def do(j):
            def op(dupe):
                j.add_progress()
                self.copy_or_move(dupe, copy, destination, desttype)

            j.start_job(self.results.mark_count)
            self.results.perform_on_marked(op, not copy)

        if not self.results.mark_count:
            self.view.show_message(MSG_NO_MARKED_DUPES)
            return
        destination = self.view.select_dest_folder(
            tr("Select a directory to copy marked files to")
            if copy
            else tr("Select a directory to move marked files to")
        )
        if destination:
            desttype = self.options["copymove_dest_type"]
            jobid = JobType.COPY if copy else JobType.MOVE
            self._start_job(jobid, do)

    def delete_marked(self):
        """Start an async job to send marked duplicates to the trash."""
        if not self.results.mark_count:
            self.view.show_message(MSG_NO_MARKED_DUPES)
            return
        if not self.deletion_options.show(self.results.mark_count):
            return
        args = [
            self.deletion_options.link_deleted,
            self.deletion_options.use_hardlinks,
            self.deletion_options.direct,
        ]
        logging.debug("Starting deletion job with args %r", args)
        self._start_job(JobType.DELETE, self._do_delete, args=args)

    def export_to_xhtml(self):
        """Export current results to XHTML.

        The configuration of the :attr:`result_table` (columns order and visibility) is used to
        determine how the data is presented in the export. In other words, the exported table in
        the resulting XHTML will look just like the results table.
        """
        colnames, rows = self._get_export_data()
        export_path = export.export_to_xhtml(colnames, rows)
        desktop.open_path(export_path)

    def export_to_csv(self):
        """Export current results to CSV.

        The columns and their order in the resulting CSV file is determined in the same way as in
        :meth:`export_to_xhtml`.
        """
        dest_file = self.view.select_dest_file(tr("Select a destination for your exported CSV"), "csv")
        if dest_file:
            colnames, rows = self._get_export_data()
            try:
                export.export_to_csv(dest_file, colnames, rows)
            except OSError as e:
                self.view.show_message(tr("Couldn't write to file: {}").format(str(e)))

    def get_display_info(self, dupe, group, delta=False):
        def empty_data():
            return {c.name: "---" for c in self.result_table.COLUMNS[1:]}

        if (dupe is None) or (group is None):
            return empty_data()
        try:
            return dupe.get_display_info(group, delta)
        except Exception as e:
            logging.warning("Exception (type: %s) on GetDisplayInfo for %s: %s", type(e), str(dupe.path), str(e))
            return empty_data()

    def invoke_custom_command(self):
        """Calls command in ``CustomCommand`` pref with ``%d`` and ``%r`` placeholders replaced.

        Using the current selection, ``%d`` is replaced with the currently selected dupe and ``%r``
        is replaced with that dupe's ref file. If there's no selection, the command is not invoked.
        If the dupe is a ref, ``%d`` and ``%r`` will be the same.
        """
        cmd = self.view.get_default("CustomCommand")
        if not cmd:
            msg = tr("You have no custom command set up. Set it up in your preferences.")
            self.view.show_message(msg)
            return
        if not self.selected_dupes:
            return
        dupes = self.selected_dupes
        refs = [self.results.get_group_of_duplicate(dupe).ref for dupe in dupes]
        for dupe, ref in zip(dupes, refs):
            dupe_cmd = cmd.replace("%d", str(dupe.path))
            dupe_cmd = dupe_cmd.replace("%r", str(ref.path))
            match = re.match(r'"([^"]+)"(.*)', dupe_cmd)
            if match is not None:
                # This code here is because subprocess. Popen doesn't seem to accept, under Windows,
                # executable paths with spaces in it, *even* when they're enclosed in "". So this is
                # a workaround to make the damn thing work.
                exepath, args = match.groups()
                path, exename = op.split(exepath)
                p = subprocess.Popen(exename + args, shell=True, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                output = p.stdout.read()
                logging.info("Custom command %s %s: %s", exename, args, output)
            else:
                p = subprocess.Popen(dupe_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                output = p.stdout.read()
                logging.info("Custom command %s: %s", dupe_cmd, output)

    def load(self):
        """Load directory selection and ignore list from files in appdata.

        This method is called during startup so that directory selection and ignore list, which
        is persistent data, is the same as when the last session was closed (when :meth:`save` was
        called).
        """
        self.directories.load_from_file(op.join(self.appdata, "last_directories.xml"))
        self.notify("directories_changed")
        p = op.join(self.appdata, "ignore_list.xml")
        self.ignore_list.load_from_xml(p)
        self.ignore_list_dialog.refresh()
        p = op.join(self.appdata, "exclude_list.xml")
        self.exclude_list.load_from_xml(p)
        self.exclude_list_dialog.refresh()

    def load_directories(self, filepath):
        # Clear out previous entries
        self.directories.__init__()
        self.directories.load_from_file(filepath)
        self.notify("directories_changed")

    def load_from(self, filename):
        """Start an async job to load results from ``filename``.

        :param str filename: path of the XML file (created with :meth:`save_as`) to load
        """

        def do(j):
            self.results.load_from_xml(filename, self._get_file, j)

        self._start_job(JobType.LOAD, do)

    def make_selected_reference(self):
        """Promote :attr:`selected_dupes` to reference position within their respective groups.

        Each selected dupe will become the :attr:`~core.engine.Group.ref` of its group. If there's
        more than one dupe selected for the same group, only the first (in the order currently shown
        in :attr:`result_table`) dupe will be promoted.
        """
        dupes = self.without_ref(self.selected_dupes)
        changed_groups = set()
        for dupe in dupes:
            g = self.results.get_group_of_duplicate(dupe)
            if g not in changed_groups and self.results.make_ref(dupe):
                changed_groups.add(g)
        # It's not always obvious to users what this action does, so to make it a bit clearer,
        # we change our selection to the ref of all changed groups. However, we also want to keep
        # the files that were ref before and weren't changed by the action. In effect, what this
        # does is that we keep our old selection, but remove all non-ref dupes from it.
        # If no group was changed, however, we don't touch the selection.
        if not self.result_table.power_marker:
            if changed_groups:
                self.selected_dupes = [
                    d for d in self.selected_dupes if self.results.get_group_of_duplicate(d).ref is d
                ]
            self.notify("results_changed")
        else:
            # If we're in "Dupes Only" mode (previously called Power Marker), things are a bit
            # different. The refs are not shown in the table, and if our operation is successful,
            # this means that there's no way to follow our dupe selection. Then, the best thing to
            # do is to keep our selection index-wise (different dupe selection, but same index
            # selection).
            self.notify("results_changed_but_keep_selection")

    def mark_all(self):
        """Set all dupes in the results as marked."""
        self.results.mark_all()
        self.notify("marking_changed")

    def mark_none(self):
        """Set all dupes in the results as unmarked."""
        self.results.mark_none()
        self.notify("marking_changed")

    def mark_invert(self):
        """Invert the marked state of all dupes in the results."""
        self.results.mark_invert()
        self.notify("marking_changed")

    def mark_dupe(self, dupe, marked):
        """Change marked status of ``dupe``.

        :param dupe: dupe to mark/unmark
        :type dupe: :class:`~core.fs.File`
        :param bool marked: True = mark, False = unmark
        """
        if marked:
            self.results.mark(dupe)
        else:
            self.results.unmark(dupe)
        self.notify("marking_changed")

    def open_selected(self):
        """Open :attr:`selected_dupes` with their associated application."""
        if len(self.selected_dupes) > 10 and not self.view.ask_yes_no(MSG_MANY_FILES_TO_OPEN):
            return
        for dupe in self.selected_dupes:
            desktop.open_path(dupe.path)

    def purge_ignore_list(self):
        """Remove files that don't exist from :attr:`ignore_list`."""
        self.ignore_list.filter(lambda f, s: op.exists(f) and op.exists(s))
        self.ignore_list_dialog.refresh()

    def remove_directories(self, indexes):
        """Remove root directories at ``indexes`` from :attr:`directories`.

        :param indexes: Indexes of the directories to remove.
        :type indexes: list of int
        """
        try:
            indexes = sorted(indexes, reverse=True)
            for index in indexes:
                del self.directories[index]
            self.notify("directories_changed")
        except IndexError:
            pass

    def remove_duplicates(self, duplicates):
        """Remove ``duplicates`` from :attr:`results`.

        Calls :meth:`~core.results.Results.remove_duplicates` and send appropriate notifications.

        :param duplicates: duplicates to remove.
        :type duplicates: list of :class:`~core.fs.File`
        """
        self.results.remove_duplicates(self.without_ref(duplicates))
        self.notify("results_changed_but_keep_selection")

    def remove_marked(self):
        """Removed marked duplicates from the results (without touching the files themselves)."""
        if not self.results.mark_count:
            self.view.show_message(MSG_NO_MARKED_DUPES)
            return
        msg = tr("You are about to remove %d files from results. Continue?")
        if not self.view.ask_yes_no(msg % self.results.mark_count):
            return
        self.results.perform_on_marked(lambda x: None, True)
        self._results_changed()

    def remove_selected(self):
        """Removed :attr:`selected_dupes` from the results (without touching the files themselves)."""
        dupes = self.without_ref(self.selected_dupes)
        if not dupes:
            self.view.show_message(MSG_NO_SELECTED_DUPES)
            return
        msg = tr("You are about to remove %d files from results. Continue?")
        if not self.view.ask_yes_no(msg % len(dupes)):
            return
        self.remove_duplicates(dupes)

    def rename_selected(self, newname):
        """Renames the selected dupes's file to ``newname``.

        If there's more than one selected dupes, the first one is used.

        :param str newname: The filename to rename the dupe's file to.
        """
        try:
            d = self.selected_dupes[0]
            d.rename(newname)
            return True
        except (IndexError, fs.FSError) as e:
            logging.warning("dupeGuru Warning: %s" % str(e))
        return False

    def reprioritize_groups(self, sort_key):
        """Sort dupes in each group (in :attr:`results`) according to ``sort_key``.

        Called by the re-prioritize dialog. Calls :meth:`~core.engine.Group.prioritize` and, once
        the sorting is done, show a message that confirms the action.

        :param sort_key: The key being sent to :meth:`~core.engine.Group.prioritize`
        :type sort_key: f(dupe)
        """
        count = 0
        for group in self.results.groups:
            if group.prioritize(key_func=sort_key):
                count += 1
        if count:
            self.results.refresh_required = True
        self._results_changed()
        msg = tr("{} duplicate groups were changed by the re-prioritization.").format(count)
        self.view.show_message(msg)

    def reveal_selected(self):
        if self.selected_dupes:
            desktop.reveal_path(self.selected_dupes[0].path)

    def save(self):
        if not op.exists(self.appdata):
            os.makedirs(self.appdata)
        self.directories.save_to_file(op.join(self.appdata, "last_directories.xml"))
        p = op.join(self.appdata, "ignore_list.xml")
        self.ignore_list.save_to_xml(p)
        p = op.join(self.appdata, "exclude_list.xml")
        self.exclude_list.save_to_xml(p)
        self.notify("save_session")

    def close(self):
        fs.filesdb.close()

    def save_as(self, filename):
        """Save results in ``filename``.

        :param str filename: path of the file to save results (as XML) to.
        """
        try:
            self.results.save_to_xml(filename)
        except OSError as e:
            self.view.show_message(tr("Couldn't write to file: {}").format(str(e)))

    def save_directories_as(self, filename):
        """Save directories in ``filename``.

        :param str filename: path of the file to save directories (as XML) to.
        """
        try:
            self.directories.save_to_file(filename)
        except OSError as e:
            self.view.show_message(tr("Couldn't write to file: {}").format(str(e)))

    def start_scanning(self, profile_scan=False):
        """Starts an async job to scan for duplicates.

        Scans folders selected in :attr:`directories` and put the results in :attr:`results`
        """
        scanner = self.SCANNER_CLASS()
        if not self.directories.has_any_file():
            self.view.show_message(tr("The selected directories contain no scannable file."))
            return
        # Send relevant options down to the scanner instance
        for k, v in self.options.items():
            if hasattr(scanner, k):
                setattr(scanner, k, v)
        if self.app_mode == AppMode.PICTURE:
            scanner.cache_path = self._get_picture_cache_path()
        self.results.groups = []
        self._recreate_result_table()
        self._results_changed()

        def do(j):
            if profile_scan:
                pr = cProfile.Profile()
                pr.enable()
            j.set_progress(0, tr("Collecting files to scan"))
            if scanner.scan_type == ScanType.FOLDERS:
                files = list(self.directories.get_folders(folderclass=se.fs.Folder, j=j))
            else:
                files = list(self.directories.get_files(fileclasses=self.fileclasses, j=j))
            if self.options["ignore_hardlink_matches"]:
                files = self._remove_hardlink_dupes(files)
            logging.info("Scanning %d files" % len(files))
            self.results.groups = scanner.get_dupe_groups(files, self.ignore_list, j)
            self.discarded_file_count = scanner.discarded_file_count
            if profile_scan:
                pr.disable()
                pr.dump_stats(op.join(self.appdata, f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.profile"))

        self._start_job(JobType.SCAN, do)

    def toggle_selected_mark_state(self):
        selected = self.without_ref(self.selected_dupes)
        if not selected:
            return
        if allsame(self.results.is_marked(d) for d in selected):
            markfunc = self.results.mark_toggle
        else:
            markfunc = self.results.mark
        for dupe in selected:
            markfunc(dupe)
        self.notify("marking_changed")

    def without_ref(self, dupes):
        """Returns ``dupes`` with all reference elements removed."""
        return [dupe for dupe in dupes if self.results.get_group_of_duplicate(dupe).ref is not dupe]

    def get_default(self, key, fallback_value=None):
        result = nonone(self.view.get_default(key), fallback_value)
        if fallback_value is not None and not isinstance(result, type(fallback_value)):
            # we don't want to end up with garbage values from the prefs
            try:
                result = type(fallback_value)(result)
            except Exception:
                result = fallback_value
        return result

    def set_default(self, key, value):
        self.view.set_default(key, value)

    # --- Properties
    @property
    def stat_line(self):
        result = self.results.stat_line
        if self.discarded_file_count:
            result = tr("%s (%d discarded)") % (result, self.discarded_file_count)
        return result

    @property
    def fileclasses(self):
        return self._get_fileclasses()

    @property
    def SCANNER_CLASS(self):
        if self.app_mode == AppMode.PICTURE:
            return pe.scanner.ScannerPE
        elif self.app_mode == AppMode.MUSIC:
            return me.scanner.ScannerME
        else:
            return se.scanner.ScannerSE

    @property
    def METADATA_TO_READ(self):
        if self.app_mode == AppMode.PICTURE:
            return ["size", "mtime", "dimensions", "exif_timestamp"]
        elif self.app_mode == AppMode.MUSIC:
            return [
                "size",
                "mtime",
                "duration",
                "bitrate",
                "samplerate",
                "title",
                "artist",
                "album",
                "genre",
                "year",
                "track",
                "comment",
            ]
        else:
            return ["size", "mtime"]
