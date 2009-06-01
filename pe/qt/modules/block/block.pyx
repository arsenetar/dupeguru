cdef object getblock(object image):
    cdef int width, height, pixel_count, red, green, blue, i, offset
    cdef char *s
    cdef unsigned char r, g, b
    width = image.width()
    height = image.height()
    if width:
        pixel_count = width * height
        red = green = blue = 0
        tmp = image.bits().asstring(image.numBytes())
        s = tmp
        for i in range(pixel_count):
            offset = i * 3
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
        top = min(ih * block_height, height - block_height)
        for iw in range(block_count_per_side):
            left = min(iw * block_width, width - block_width)
            crop = image.copy(left, top, block_width, block_height)
            result.append(getblock(crop))
    return result
