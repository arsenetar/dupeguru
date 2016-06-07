The scanning process
====================

.. contents::

dupeGuru has 3 basic ways of scanning: :ref:`worded-scan` and :ref:`contents-scan` and
:ref:`picture blocks <picture-blocks-scan>`. The first two types are for the Standard and Music
modes, the last is for the Picture mode. The scanning process is configured through the
:doc:`Preference pane <preferences>`.

.. _worded-scan:

Worded scans
------------

Worded scans extract a string from each file and split it into words. The string can come from two
different sources: **Filename** or **Tags** (Music Edition only).

When our source is music tags, we have to choose which tags to use. If, for example, we choose to
analyse *artist* and *title* tags, we'd end up with strings like
"The White Stripes - Seven Nation Army".

Words are split by space characters, with all punctuation removed (some are replaced by spaces, some
by nothing) and all words lowercased. For example, the string "This guy's song(remix)" yields
*this*, *guys*, *song* and *remix*.

Once this is done, the scanning dance begins. Finding duplicates is only a matter of finding how
many words in common two given strings have. If the :ref:`filter hardness <filter-hardness>` is,
for example, ``80``, it means that 80% of the words of two strings must match. To determine the
matching percentage, dupeGuru first counts the total number of words in **both** strings, then count
the number of words matching (every word matching count as 2), and then divide the number of words
matching by the total number of words. If the result is higher or equal than the filter hardness,
we have a duplicate match. For example, "a b c d" and "c d e" have a matching percentage of 57
(4 words matching, 7 total words).

Fields
^^^^^^

Song filenames often come with multiple and distinct parts and this can cause problems. For example,
let's take these two songs: "Dolly Parton - I Will Always Love You" and
"Whitney Houston - I Will Always Love You". They are clearly not the same song (they come from
different artists), but they still still have a matching score of 71%! This means that, with a naive
scanning method, we would get these songs as a false positive as soon as we try to dig a bit deeper
in our dupe hunt by lowering the threshold a bit.

This is why we have the "Fields" concept. Fields are separated by dashes (``-``). When the
"Filename - Fields" scan type is chosen, each field is compared separately. Our final matching score
will only be the lowest of all the fields. In our example, the title has a 100% match, but the
artist has a 0% match, making our final match score 0.

Sometimes, our song filename policy isn't completely homogenous, which means that we can end up with
"The White Stripes - Seven Nation Army" and "Seven Nation Army - The White Stripes". This is why
we have the "Filename - Fields (No Order)" scan type. With this scan type, all fields are compared
with each other, and the highest score is kept. Then, the final matching score is the lowest of them
all. In our case, the final matching score is 100.

Note: Each field is used once. Thus, "The White Stripes - The White Stripes" and
"The White Stripes - Seven Nation Army" have a match score of 0 because the second
"The White Stripes" can't be compared with the first field of the other name because it has already
been "used up" by the first field. Our final match score would be 0.

*Tags* scanning method is always "fielded". When choosing this scan method, we also choose which
tags are going to be compared, each being a field.

.. _word-weighting:

Word weighting
^^^^^^^^^^^^^^

When enabled, this option slightly changes how matching percentage is calculated by making bigger
words worth more. With word weighting, instead of having a value of 1 in the duplicate count and
total word count, every word have a value equal to the number of characters they have. With word
weighting, "ab cde fghi" and "ab cde fghij" would have a matching percentage of 53% (19 total
characters, 10 characters matching (4 for "ab" and 6 for "cde")).

.. _similarity-matching:

Similarity matching
^^^^^^^^^^^^^^^^^^^

When enabled, similar words will be counted as matches. For example "The White Stripes" and
"The White Stripe" would have a match score of 100 instead of 66 with that option turned on.

Two words are considered similar if they can be made equal with only a few edit operations (removing
a letter, adding one etc.). The process used is not unlike the
`Levenshtein distance`_. For the technically inclined, the actual function used is
Python's `get_close_matches`_ with a ``0.8`` cutoff.

**Warning:** Use this option with caution. It is likely that you will get a lot of false positives
in your results when turning it on. However, it will help you to find duplicates that you wouldn't
have found otherwise. The scan process also is significantly slower with this option turned on.

.. _contents-scan:

Contents scans
--------------

Contents scans are much simpler than worded scans. We read files and if the contents is exactly the
same, we consider the two files duplicates.

This is, of course, quite longer than comparing filenames and, to avoid needlessly reading whole
file contents, we start by looking at file sizes. After having grouped our files by size, we discard
every file that is alone in its group. Then, we proceed to read the contents of our remaining files.

MD5 hashes are used to compute compare contents. Yes, it is widely known that forging files having
the same MD5 hash is easy, but this file has to be knowingly forged. The possibilities of two files
having the same MD5 hash *and* the same size by accident is still very, very small.

The :ref:`filter hardness <filter-hardness>` preference is ignored in this scan.

Folders
^^^^^^^

This is a special Contents scan type. It works like a normal contents scan, but
instead of trying to find duplicate files, it tries to find duplicate folders.
A folder is duplicate to another if all files it contains have the same
contents as the other folder's file.

This scan is, of course, recursive and subfolders are checked. dupeGuru keeps only the biggest
fishes. Therefore, if two folders that are considered as matching contain subfolders, these
subfolders will not be included in the final results.

With this mode, we end up with folders as results instead of files.

.. _picture-blocks-scan:

Picture blocks
--------------

dupeGuru Picture mode stands apart of its two friends. Its scan types are completely different.
The first one is its "Contents" scan, which is a bit too generic, hence the name we use here,
"Picture blocks".

We start by opening every picture in RGB bitmap mode, then we "blockify" the picture. We create a
15x15 grid and compute the average color of each grid tile. This is the "picture analysis" phase.
It's very time consuming and the result is cached in a database (the "picture cache").

Once we've done that, we can start comparing them. Each tile in the grid (an average color) is
compared to its corresponding grid on the other picture and a color diff is computer (it's simply
a sum of the difference of R, G and B on each side). All these sums are added up to a final "score".

If that score is smaller or equal to ``100 - threshold``, we have a match.

A threshold of 100 adds an additional constraint that pictures have to be exactly the same (it's
possible, due to averaging, that the tile comparison yields ``0`` for pictures that aren't exactly
the same, but since "100%" suggests "exactly the same", we discard those ocurrences). If you want
to get pictures that are very, very similar but still allow a bit of fuzzy differences, go for 99%.

This second part of the scan is CPU intensive and can take quite a bit of time. This task has been
made to take advatange of multi-core CPUs and has been optimized to the best of my abilities, but
the fact of the matter is that, due to the fuzziness of the task, we still have to compare every picture
to every other, making the algorithm quadratic (if ``N`` is the number of pictures to compare, the
number of comparisons to perform is ``N*N``).

This algorithm is very naive, but in the field, it works rather well. If you master a better
algorithm and want to improve dupeGuru, by all means, let me know!

EXIF Timestamp
--------------

This one is easy. We read the EXIF information of every picture and extract the ``DateTimeOriginal``
tag. If the tag is the same for two pictures, they're considered duplicates.

**Warning:** Modified pictures often keep the same EXIF timestamp, so watch out for false positives
when you use that scan type.

.. _Levenshtein distance: http://en.wikipedia.org/wiki/Levenshtein_distance
.. _get_close_matches: http://docs.python.org/3/library/difflib.html#difflib.get_close_matches
