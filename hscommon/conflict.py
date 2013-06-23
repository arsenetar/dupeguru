# Created By: Virgil Dupras
# Created On: 2008-01-08
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import re
from . import io

#This matches [123], but not [12] (3 digits being the minimum).
#It also matches [1234] [12345] etc..
#And only at the start of the string
re_conflict = re.compile(r'^\[\d{3}\d*\] ')

def get_conflicted_name(other_names, name):
    """Returns name with a [000] number in front of it.
    
    The number between brackets depends on how many conlicted filenames
    there already are in other_names.
    """
    name = get_unconflicted_name(name)
    if name not in other_names:
        return name
    i = 0
    while True:
        newname = '[%03d] %s' % (i, name)
        if newname not in other_names:
            return newname
        i += 1

def get_unconflicted_name(name):
    return re_conflict.sub('',name,1)

def is_conflicted(name):
    return re_conflict.match(name) is not None

def _smart_move_or_copy(operation, source_path, dest_path):
    ''' Use move() or copy() to move and copy file with the conflict management, but without the
        slowness of the fs system.
    '''
    if io.isdir(dest_path) and not io.isdir(source_path):
        dest_path = dest_path + source_path[-1]
    if io.exists(dest_path):
        filename = dest_path[-1]
        dest_dir_path = dest_path[:-1]
        newname = get_conflicted_name(io.listdir(dest_dir_path), filename)
        dest_path = dest_dir_path + newname
    operation(source_path, dest_path)
    
def smart_move(source_path, dest_path):
    _smart_move_or_copy(io.move, source_path, dest_path)

def smart_copy(source_path, dest_path):
    try:
        _smart_move_or_copy(io.copy, source_path, dest_path)
    except IOError as e:
        if e.errno in {21, 13}: # it's a directory, code is 21 on OS X / Linux and 13 on Windows
            _smart_move_or_copy(io.copytree, source_path, dest_path)
        else:
            raise