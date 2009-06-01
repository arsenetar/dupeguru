# Created By: Virgil Dupras
# Created On: 2009-04-23
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

cdef extern from "stdlib.h":
    int abs(int n) # required so that abs() is applied on ints, not python objects

class NoBlocksError(Exception):
    """avgdiff/maxdiff has been called with empty lists"""

class DifferentBlockCountError(Exception):
    """avgdiff/maxdiff has been called with 2 block lists of different size."""


cdef object getblock(object image):
    """Returns a 3 sized tuple containing the mean color of 'image'.
    
    image: a PIL image or crop.
    """
    cdef int pixel_count, red, green, blue, r, g, b
    if image.size[0]:
        pixel_count = image.size[0] * image.size[1]
        red = green = blue = 0
        for r, g, b in image.getdata():
            red += r
            green += g
            blue += b
        return (red // pixel_count, green // pixel_count, blue // pixel_count)
    else:
        return (0, 0, 0)

def getblocks2(image, int block_count_per_side):
    """Returns a list of blocks (3 sized tuples).
    
    image: A PIL image to base the blocks on.
    block_count_per_side: This integer determine the number of blocks the function will return.
    If it is 10, for example, 100 blocks will be returns (10 width, 10 height). The blocks will not
    necessarely cover square areas. The area covered by each block will be proportional to the image
    itself.
    """
    if not image.size[0]:
        return []
    cdef int width, height, block_width, block_height, ih, iw, top, bottom, left, right
    width, height = image.size
    block_width = max(width // block_count_per_side, 1)
    block_height = max(height // block_count_per_side, 1)
    result = []
    for ih in range(block_count_per_side):
        top = min(ih * block_height, height - block_height)
        bottom = top + block_height
        for iw in range(block_count_per_side):
            left = min(iw * block_width, width - block_width)
            right = left + block_width
            box = (left, top, right, bottom)
            crop = image.crop(box)
            result.append(getblock(crop))
    return result

cdef int diff(first, second):
    """Returns the difference between the first block and the second.
    
    It returns an absolute sum of the 3 differences (RGB).
    """
    cdef int r1, g1, b1, r2, g2, b2
    r1, g1, b1 = first
    r2, g2, b2 = second
    return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)

def avgdiff(first, second, int limit, int min_iterations):
    """Returns the average diff between first blocks and seconds.
    
    If the result surpasses limit, limit + 1 is returned, except if less than min_iterations
    iterations have been made in the blocks.
    """
    cdef int count, sum, i, iteration_count
    count = len(first)
    if count != len(second):
        raise DifferentBlockCountError()
    if not count:
        raise NoBlocksError()
    sum = 0
    for i in range(count):
        iteration_count = i + 1
        item1 = first[i]
        item2 = second[i]
        sum += diff(item1, item2)
        if sum > limit * iteration_count and iteration_count >= min_iterations:
            return limit + 1
    result = sum // count
    if (not result) and sum:
        result = 1
    return result