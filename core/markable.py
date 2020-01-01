# Created By: Virgil Dupras
# Created On: 2006/02/23
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html


class Markable:
    def __init__(self):
        self.__marked = set()
        self.__inverted = False

    # ---Virtual
    # About did_mark and did_unmark: They only happen what an object is actually added/removed
    # in self.__marked, and is not affected by __inverted. Thus, self.mark while __inverted
    # is True will launch _DidUnmark.
    def _did_mark(self, o):
        pass

    def _did_unmark(self, o):
        pass

    def _get_markable_count(self):
        return 0

    def _is_markable(self, o):
        return True

    # ---Protected
    def _remove_mark_flag(self, o):
        try:
            self.__marked.remove(o)
            self._did_unmark(o)
        except KeyError:
            pass

    # ---Public
    def is_marked(self, o):
        if not self._is_markable(o):
            return False
        is_marked = o in self.__marked
        if self.__inverted:
            is_marked = not is_marked
        return is_marked

    def mark(self, o):
        if self.is_marked(o):
            return False
        if not self._is_markable(o):
            return False
        return self.mark_toggle(o)

    def mark_multiple(self, objects):
        for o in objects:
            self.mark(o)

    def mark_all(self):
        self.mark_none()
        self.__inverted = True

    def mark_invert(self):
        self.__inverted = not self.__inverted

    def mark_none(self):
        for o in self.__marked:
            self._did_unmark(o)
        self.__marked = set()
        self.__inverted = False

    def mark_toggle(self, o):
        try:
            self.__marked.remove(o)
            self._did_unmark(o)
        except KeyError:
            if not self._is_markable(o):
                return False
            self.__marked.add(o)
            self._did_mark(o)
        return True

    def mark_toggle_multiple(self, objects):
        for o in objects:
            self.mark_toggle(o)

    def unmark(self, o):
        if not self.is_marked(o):
            return False
        return self.mark_toggle(o)

    def unmark_multiple(self, objects):
        for o in objects:
            self.unmark(o)

    # --- Properties
    @property
    def mark_count(self):
        if self.__inverted:
            return self._get_markable_count() - len(self.__marked)
        else:
            return len(self.__marked)

    @property
    def mark_inverted(self):
        return self.__inverted


class MarkableList(list, Markable):
    def __init__(self):
        list.__init__(self)
        Markable.__init__(self)

    def _get_markable_count(self):
        return len(self)

    def _is_markable(self, o):
        return o in self
