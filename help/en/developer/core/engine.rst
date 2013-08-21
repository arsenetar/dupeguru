core.engine
===========

.. automodule:: core.engine
    
    .. autoclass:: Match
    
    .. autoclass:: Group
        :members:
    
    .. autofunction:: build_word_dict
    .. autofunction:: compare
    .. autofunction:: compare_fields
    .. autofunction:: getmatches
    .. autofunction:: getmatches_by_contents
    .. autofunction:: get_groups
    .. autofunction:: merge_similar_words
    .. autofunction:: reduce_common_words
    
.. _fields:

Fields
------

Fields are groups of words which each represent a significant part of the whole name. This concept
is sifnificant in music file names, where we often have names like "My Artist - a very long title
with many many words".

This title has 10 words. If you run as scan with a bit of tolerance, let's say 90%, you'll be able
to find a dupe that has only one "many" in the song title. However, you would also get false
duplicates from a title like "My Giraffe - a very long title with many many words", which is of
course a very different song and it doesn't make sense to match them.

When matching by fields, each field (separated by "-") is considered as a separate string to match
independently. After all fields are matched, the lowest result is kept. In the "Giraffe" example we
gave, the result would be 50% instead of 90% in normal mode.
