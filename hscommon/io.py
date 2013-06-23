# Created By: Virgil Dupras
# Created On: 2007-10-23
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# HS code should only deal with Path instances, not string paths. One of the annoyances of this
# is to always have to convert Path instances with unicode() when calling open() or listdir() etc..
# this unit takes care of this

import builtins
import os
import os.path
import shutil
import logging

def log_io_error(func):
    """ Catches OSError, IOError and WindowsError and log them
    """
    def wrapper(path, *args, **kwargs):
        try:
            return func(path, *args, **kwargs)
        except (IOError, OSError) as e:
            msg = 'Error "{0}" during operation "{1}" on "{2}": "{3}"'
            classname = e.__class__.__name__
            funcname = func.__name__
            logging.warn(msg.format(classname, funcname, str(path), str(e)))
    
    return wrapper

def copy(source_path, dest_path):
    return shutil.copy(str(source_path), str(dest_path))

def copytree(source_path, dest_path, *args, **kwargs):
    return shutil.copytree(str(source_path), str(dest_path), *args, **kwargs)

def exists(path):
    return os.path.exists(str(path))

def isdir(path):
    return os.path.isdir(str(path))

def isfile(path):
    return os.path.isfile(str(path))

def islink(path):
    return os.path.islink(str(path))

def listdir(path):
    return os.listdir(str(path))

def mkdir(path, *args, **kwargs):
    return os.mkdir(str(path), *args, **kwargs)

def makedirs(path, *args, **kwargs):
    return os.makedirs(str(path), *args, **kwargs)

def move(source_path, dest_path):
    return shutil.move(str(source_path), str(dest_path))

def open(path, *args, **kwargs):
    return builtins.open(str(path), *args, **kwargs)

def remove(path):
    return os.remove(str(path))

def rename(source_path, dest_path):
    return os.rename(str(source_path), str(dest_path))

def rmdir(path):
    return os.rmdir(str(path))

def rmtree(path):
    return shutil.rmtree(str(path))

def stat(path):
    return os.stat(str(path))
