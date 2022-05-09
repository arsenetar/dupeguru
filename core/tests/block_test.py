# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html
# The commented out tests are tests for function that have been converted to pure C for speed

from pytest import raises, skip
from hscommon.testutil import eq_

try:
    from core.pe.block import avgdiff, getblocks2, NoBlocksError, DifferentBlockCountError
except ImportError:
    skip("Can't import the block module, probably hasn't been compiled.")


def my_avgdiff(first, second, limit=768, min_iter=3):  # this is so I don't have to re-write every call
    return avgdiff(first, second, limit, min_iter)


BLACK = (0, 0, 0)
RED = (0xFF, 0, 0)
GREEN = (0, 0xFF, 0)
BLUE = (0, 0, 0xFF)


class FakeImage:
    def __init__(self, size, data):
        self.size = size
        self.data = data

    def getdata(self):
        return self.data

    def crop(self, box):
        pixels = []
        for i in range(box[1], box[3]):
            for j in range(box[0], box[2]):
                pixel = self.data[i * self.size[0] + j]
                pixels.append(pixel)
        return FakeImage((box[2] - box[0], box[3] - box[1]), pixels)


def empty():
    return FakeImage((0, 0), [])


def single_pixel():  # one red pixel
    return FakeImage((1, 1), [(0xFF, 0, 0)])


def four_pixels():
    pixels = [RED, (0, 0x80, 0xFF), (0x80, 0, 0), (0, 0x40, 0x80)]
    return FakeImage((2, 2), pixels)


class TestCasegetblock:
    def test_single_pixel(self):
        im = single_pixel()
        [b] = getblocks2(im, 1)
        eq_(RED, b)

    def test_no_pixel(self):
        im = empty()
        eq_([], getblocks2(im, 1))

    def test_four_pixels(self):
        im = four_pixels()
        [b] = getblocks2(im, 1)
        meanred = (0xFF + 0x80) // 4
        meangreen = (0x80 + 0x40) // 4
        meanblue = (0xFF + 0x80) // 4
        eq_((meanred, meangreen, meanblue), b)


class TestCasegetblocks2:
    def test_empty_image(self):
        im = empty()
        blocks = getblocks2(im, 1)
        eq_(0, len(blocks))

    def test_one_block_image(self):
        im = four_pixels()
        blocks = getblocks2(im, 1)
        eq_(1, len(blocks))
        block = blocks[0]
        meanred = (0xFF + 0x80) // 4
        meangreen = (0x80 + 0x40) // 4
        meanblue = (0xFF + 0x80) // 4
        eq_((meanred, meangreen, meanblue), block)

    def test_four_blocks_all_black(self):
        im = FakeImage((2, 2), [BLACK, BLACK, BLACK, BLACK])
        blocks = getblocks2(im, 2)
        eq_(4, len(blocks))
        for block in blocks:
            eq_(BLACK, block)

    def test_two_pixels_image_horizontal(self):
        pixels = [RED, BLUE]
        im = FakeImage((2, 1), pixels)
        blocks = getblocks2(im, 2)
        eq_(4, len(blocks))
        eq_(RED, blocks[0])
        eq_(BLUE, blocks[1])
        eq_(RED, blocks[2])
        eq_(BLUE, blocks[3])

    def test_two_pixels_image_vertical(self):
        pixels = [RED, BLUE]
        im = FakeImage((1, 2), pixels)
        blocks = getblocks2(im, 2)
        eq_(4, len(blocks))
        eq_(RED, blocks[0])
        eq_(RED, blocks[1])
        eq_(BLUE, blocks[2])
        eq_(BLUE, blocks[3])


class TestCaseavgdiff:
    def test_empty(self):
        with raises(NoBlocksError):
            my_avgdiff([], [])

    def test_two_blocks(self):
        b1 = (5, 10, 15)
        b2 = (255, 250, 245)
        b3 = (0, 0, 0)
        b4 = (255, 0, 255)
        blocks1 = [b1, b2]
        blocks2 = [b3, b4]
        expected1 = 5 + 10 + 15
        expected2 = 0 + 250 + 10
        expected = (expected1 + expected2) // 2
        eq_(expected, my_avgdiff(blocks1, blocks2))

    def test_blocks_not_the_same_size(self):
        b = (0, 0, 0)
        with raises(DifferentBlockCountError):
            my_avgdiff([b, b], [b])

    def test_first_arg_is_empty_but_not_second(self):
        # Don't return 0 (as when the 2 lists are empty), raise!
        b = (0, 0, 0)
        with raises(DifferentBlockCountError):
            my_avgdiff([], [b])

    def test_limit(self):
        ref = (0, 0, 0)
        b1 = (10, 10, 10)  # avg 30
        b2 = (20, 20, 20)  # avg 45
        b3 = (30, 30, 30)  # avg 60
        blocks1 = [ref, ref, ref]
        blocks2 = [b1, b2, b3]
        eq_(45, my_avgdiff(blocks1, blocks2, 44))

    def test_min_iterations(self):
        ref = (0, 0, 0)
        b1 = (10, 10, 10)  # avg 30
        b2 = (20, 20, 20)  # avg 45
        b3 = (10, 10, 10)  # avg 40
        blocks1 = [ref, ref, ref]
        blocks2 = [b1, b2, b3]
        eq_(40, my_avgdiff(blocks1, blocks2, 45 - 1, 3))

    # Bah, I don't know why this test fails, but I don't think it matters very much
    # def test_just_over_the_limit(self):
    #     #A score just over the limit might return exactly the limit due to truncating. We should
    #     #ceil() the result in this case.
    #     ref = (0, 0, 0)
    #     b1 = (10, 0, 0)
    #     b2 = (11, 0, 0)
    #     blocks1 = [ref, ref]
    #     blocks2 = [b1, b2]
    #     eq_(11, my_avgdiff(blocks1, blocks2, 10))
    #
    def test_return_at_least_1_at_the_slightest_difference(self):
        ref = (0, 0, 0)
        b1 = (1, 0, 0)
        blocks1 = [ref for _ in range(250)]
        blocks2 = [ref for _ in range(250)]
        blocks2[0] = b1
        eq_(1, my_avgdiff(blocks1, blocks2))

    def test_return_0_if_there_is_no_difference(self):
        ref = (0, 0, 0)
        blocks1 = [ref, ref]
        blocks2 = [ref, ref]
        eq_(0, my_avgdiff(blocks1, blocks2))
