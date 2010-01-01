# Created By: Virgil Dupras
# Created On: 2006/03/15
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.str import format_time, FT_DECIMAL, format_size

import time

def format_path(p):
    return unicode(p[:-1])

def format_timestamp(t, delta):
    if delta:
        return format_time(t, FT_DECIMAL)
    else:
        if t > 0:
            return time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(t))
        else:
            return '---'

def format_words(w):
    def do_format(w):
        if isinstance(w, list):
            return '(%s)' % ', '.join(do_format(item) for item in w)
        else:
            return w.replace('\n', ' ')
    
    return ', '.join(do_format(item) for item in w)

def format_perc(p):
    return "%0.0f" % p

def format_dupe_count(c):
    return str(c) if c else '---'

def cmp_value(value):
    return value.lower() if isinstance(value, basestring) else value
