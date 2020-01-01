# Created On: 2012-05-30
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os

from hscommon.gui.base import GUIObject
from hscommon.trans import tr


class DeletionOptionsView:
    """Expected interface for :class:`DeletionOptions`'s view.

    *Not actually used in the code. For documentation purposes only.*

    Our view presents the user with an appropriate way (probably a mix of checkboxes and radio
    buttons) to set the different flags in :class:`DeletionOptions`. Note that
    :attr:`DeletionOptions.use_hardlinks` is only relevant if :attr:`DeletionOptions.link_deleted`
    is true. This is why we toggle the "enabled" state of that flag.

    We expect the view to set :attr:`DeletionOptions.link_deleted` immediately as the user changes
    its value because it will toggle :meth:`set_hardlink_option_enabled`

    Other than the flags, there's also a prompt message which has a dynamic content, defined by
    :meth:`update_msg`.
    """

    def update_msg(self, msg: str):
        """Update the dialog's prompt with ``str``.
        """

    def show(self):
        """Show the dialog in a modal fashion.

        Returns whether the dialog was "accepted" (the user pressed OK).
        """

    def set_hardlink_option_enabled(self, is_enabled: bool):
        """Enable or disable the widget controlling :attr:`DeletionOptions.use_hardlinks`.
        """


class DeletionOptions(GUIObject):
    """Present the user with deletion options before proceeding.

    When the user activates "Send to trash", we present him with a couple of options that changes
    the behavior of that deletion operation.
    """

    def __init__(self):
        GUIObject.__init__(self)
        #: Whether symlinks or hardlinks are used when doing :attr:`link_deleted`.
        #: *bool*. *get/set*
        self.use_hardlinks = False
        #: Delete dupes directly and don't send to trash.
        #: *bool*. *get/set*
        self.direct = False

    def show(self, mark_count):
        """Prompt the user with a modal dialog offering our deletion options.

        :param int mark_count: Number of dupes marked for deletion.
        :rtype: bool
        :returns: Whether the user accepted the dialog (we cancel deletion if false).
        """
        self._link_deleted = False
        self.view.set_hardlink_option_enabled(False)
        self.use_hardlinks = False
        self.direct = False
        msg = tr("You are sending {} file(s) to the Trash.").format(mark_count)
        self.view.update_msg(msg)
        return self.view.show()

    def supports_links(self):
        """Returns whether our platform supports symlinks.
        """
        # When on a platform that doesn't implement it, calling os.symlink() (with the wrong number
        # of arguments) raises NotImplementedError, which allows us to gracefully check for the
        # feature.
        try:
            os.symlink()
        except NotImplementedError:
            # Windows XP, not supported
            return False
        except OSError:
            # Vista+, symbolic link privilege not held
            return False
        except TypeError:
            # wrong number of arguments
            return True

    @property
    def link_deleted(self):
        """Replace deleted dupes with symlinks (or hardlinks) to the dupe group reference.

        *bool*. *get/set*

        Whether the link is a symlink or hardlink is decided by :attr:`use_hardlinks`.
        """
        return self._link_deleted

    @link_deleted.setter
    def link_deleted(self, value):
        self._link_deleted = value
        hardlinks_enabled = value and self.supports_links()
        self.view.set_hardlink_option_enabled(hardlinks_enabled)
