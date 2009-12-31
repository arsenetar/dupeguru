# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

cdef object getblock(object image):
    cdef int width, height, pixel_count, red, green, blue, i, offset, bytes_per_line
    cdef char *s
    cdef unsigned char r, g, b
    width = image.width()
    height = image.height()
    if width:
        pixel_count = width * height
        red = green = blue = 0
        bytes_per_line = image.bytesPerLine()
        tmp = image.bits().asstring(image.numBytes())
        s = tmp
        # Qt aligns all its lines on 32bit, which means that if the number of bytes per
        # line for image is not divisible by 4, there's going to be crap inserted in "s"
        # We have to take this into account when calculating offsets
        for i in range(height):
            for j in range(width):
                offset = i * bytes_per_line + j * 3
                r = s[offset]
                g = s[offset + 1]
                b = s[offset + 2]
                red += r
                green += g
                blue += b
        return (red // pixel_count, green // pixel_count, blue // pixel_count)
    else:
        return (0, 0, 0)

def getblocks(image, int block_count_per_side):
    cdef int width, height, block_width, block_height, ih, iw, top, left
    width = image.width()
    height = image.height()
    if not width:
        return []
    block_width = max(width // block_count_per_side, 1)
    block_height = max(height // block_count_per_side, 1)
    result = []
    for ih in range(block_count_per_side):
        top = min(ih*block_height, height-block_height-1)
        for iw in range(block_count_per_side):
            left = min(iw*block_width, width-block_width-1)
            crop = image.copy(left, top, block_width, block_height)
            result.append(getblock(crop))
    return result
