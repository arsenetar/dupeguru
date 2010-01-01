# Created By: Virgil Dupras
# Created On: 2009-04-23
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# ok, this is hacky and stuff, but I don't know C well enough to play with char buffers, copy
# them around and stuff
cdef int xchar_to_int(char c):
    if 48 <= c <= 57: # 0-9
        return c - 48
    elif 65 <= c <= 70: # A-F
        return c - 55
    elif 97 <= c <= 102: # a-f
        return c - 87

def string_to_colors(s):
    """Transform the string 's' in a list of 3 sized tuples.
    """
    result = []
    cdef int i, char_count, r, g, b
    cdef char* cs
    char_count = len(s)
    char_count = (char_count // 6) * 6
    cs = s
    for i in range(0, char_count, 6):
        r = xchar_to_int(cs[i]) << 4
        r += xchar_to_int(cs[i+1])
        g = xchar_to_int(cs[i+2]) << 4
        g += xchar_to_int(cs[i+3])
        b = xchar_to_int(cs[i+4]) << 4
        b += xchar_to_int(cs[i+5])
        result.append((r, g, b))
    return result
