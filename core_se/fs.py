# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-23
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import hashlib

from hsutil import io
from hsutil.misc import nonone

from core import fs

class Bundle(fs.File):
    """This class is for Mac OSX bundles (.app). Bundles are seen by the OS as
    normal directories, but I don't want that in dupeGuru. I want dupeGuru
    to see them as files.
    """
    def _read_info(self, field):
        if field in ('size', 'ctime', 'mtime'):
            files = fs.get_all_files(self.path)
            size = sum((file.size for file in files), 0)
            self.size = size
            stats = io.stat(self.path)
            self.ctime = nonone(stats.st_ctime, 0)
            self.mtime = nonone(stats.st_mtime, 0)
        elif field in ('md5', 'md5partial'):
            # What's sensitive here is that we must make sure that subfiles'
            # md5 are always added up in the same order, but we also want a
            # different md5 if a file gets moved in a different subdirectory.
            def get_dir_md5_concat():
                files = fs.get_all_files(self.path)
                files.sort(key=lambda f:f.path)
                md5s = [getattr(f, field) for f in files]
                return ''.join(md5s)
            
            md5 = hashlib.md5(get_dir_md5_concat())
            digest = md5.digest()
            setattr(self, field, digest)
