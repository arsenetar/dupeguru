# Created By: Virgil Dupras
# Created On: 2006/09/01
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from core.pe._block import NoBlocksError, DifferentBlockCountError, avgdiff, getblocks2  # NOQA

# Converted to C
# def getblock(image):
#     """Returns a 3 sized tuple containing the mean color of 'image'.
#
#     image: a PIL image or crop.
#     """
#     if image.size[0]:
#         pixel_count = image.size[0] * image.size[1]
#         red = green = blue = 0
#         for r,g,b in image.getdata():
#             red += r
#             green += g
#             blue += b
#         return (red // pixel_count, green // pixel_count, blue // pixel_count)
#     else:
#         return (0,0,0)

# This is not used anymore
# def getblocks(image,blocksize):
#     """Returns a list of blocks (3 sized tuples).
#
#     image: A PIL image to base the blocks on.
#     blocksize: The size of the blocks to be create. This is a single integer, defining
#         both width and height (blocks are square).
#     """
#     if min(image.size) < blocksize:
#         return ()
#     result = []
#     for i in xrange(image.size[1] // blocksize):
#         for j in xrange(image.size[0] // blocksize):
#             box = (blocksize * j, blocksize * i, blocksize * (j + 1), blocksize * (i + 1))
#             crop = image.crop(box)
#             result.append(getblock(crop))
#     return result

# Converted to C
# def getblocks2(image,block_count_per_side):
#     """Returns a list of blocks (3 sized tuples).
#
#     image: A PIL image to base the blocks on.
#     block_count_per_side: This integer determine the number of blocks the function will return.
#     If it is 10, for example, 100 blocks will be returns (10 width, 10 height). The blocks will not
#     necessarely cover square areas. The area covered by each block will be proportional to the image
#     itself.
#     """
#     if not image.size[0]:
#         return []
#     width,height = image.size
#     block_width = max(width // block_count_per_side,1)
#     block_height = max(height // block_count_per_side,1)
#     result = []
#     for ih in range(block_count_per_side):
#         top = min(ih * block_height, height - block_height)
#         bottom = top + block_height
#         for iw in range(block_count_per_side):
#             left = min(iw * block_width, width - block_width)
#             right = left + block_width
#             box = (left,top,right,bottom)
#             crop = image.crop(box)
#             result.append(getblock(crop))
#     return result

# Converted to C
# def diff(first, second):
#     """Returns the difference between the first block and the second.
#
#     It returns an absolute sum of the 3 differences (RGB).
#     """
#     r1, g1, b1 = first
#     r2, g2, b2 = second
#     return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)

# Converted to C
# def avgdiff(first, second, limit=768, min_iterations=1):
#     """Returns the average diff between first blocks and seconds.
#
#     If the result surpasses limit, limit + 1 is returned, except if less than min_iterations
#     iterations have been made in the blocks.
#     """
#     if len(first) != len(second):
#         raise DifferentBlockCountError
#     if not first:
#         raise NoBlocksError
#     count = len(first)
#     sum = 0
#     zipped = izip(xrange(1, count + 1), first, second)
#     for i, first, second in zipped:
#         sum += diff(first, second)
#         if sum > limit * i and i >= min_iterations:
#             return limit + 1
#     result = sum // count
#     if (not result) and sum:
#         result = 1
#     return result

# This is not used anymore
# def maxdiff(first,second,limit=768):
#     """Returns the max diff between first blocks and seconds.
#
#     If the result surpasses limit, the first max being over limit is returned.
#     """
#     if len(first) != len(second):
#         raise DifferentBlockCountError
#     if not first:
#         raise NoBlocksError
#     result = 0
#     zipped = zip(first,second)
#     for first,second in zipped:
#         result = max(result,diff(first,second))
#         if result > limit:
#             return result
#     return result
