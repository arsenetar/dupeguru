# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from ._cache import string_to_colors  # noqa


def colors_to_string(colors):
    """Transform the 3 sized tuples 'colors' into a hex string.

    [(0,100,255)] --> 0064ff
    [(1,2,3),(4,5,6)] --> 010203040506
    """
    return "".join("%02x%02x%02x" % (r, g, b) for r, g, b in colors)


# This function is an important bottleneck of dupeGuru PE. It has been converted to C.
# def string_to_colors(s):
#     """Transform the string 's' in a list of 3 sized tuples.
#     """
#     result = []
#     for i in xrange(0, len(s), 6):
#         number = int(s[i:i+6], 16)
#         result.append((number >> 16, (number >> 8) & 0xff, number & 0xff))
#     return result
