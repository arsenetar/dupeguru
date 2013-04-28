# Created On: 2012-05-30
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.gui.base import GUIObject
from hscommon.trans import tr

class DeletionOptions(GUIObject):
    #--- View interface
    # update_msg(msg: str)
    # show()
    #
    
    def show(self, mark_count):
        self.link_deleted = False
        self.use_hardlinks = False
        self.direct = False
        msg = tr("You are sending {} file(s) to the Trash.").format(mark_count)
        self.view.update_msg(msg)
        return self.view.show()
    
