# Created By: Virgil Dupras
# Created On: 2009-05-10
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from ._block_qt import getblocks  # NOQA

# Converted to C
# def getblock(image):
#     width = image.width()
#     height = image.height()
#     if width:
#         pixel_count = width * height
#         red = green = blue = 0
#         s = image.bits().asstring(image.numBytes())
#         for i in xrange(pixel_count):
#             offset = i * 3
#             red += ord(s[offset])
#             green += ord(s[offset + 1])
#             blue += ord(s[offset + 2])
#         return (red // pixel_count, green // pixel_count, blue // pixel_count)
#     else:
#         return (0, 0, 0)
#
# def getblocks(image, block_count_per_side):
#     width = image.width()
#     height = image.height()
#     if not width:
#         return []
#     block_width = max(width // block_count_per_side, 1)
#     block_height = max(height // block_count_per_side, 1)
#     result = []
#     for ih in xrange(block_count_per_side):
#         top = min(ih * block_height, height - block_height)
#         for iw in range(block_count_per_side):
#             left = min(iw * block_width, width - block_width)
#             crop = image.copy(left, top, block_width, block_height)
#             result.append(getblock(crop))
#     return result
