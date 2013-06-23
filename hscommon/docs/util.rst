========================================
:mod:`util` - Miscellaneous utilities
========================================

.. module:: misc

.. function:: nonone(value, replace_value)
    
    Returns ``value`` if value is not None. Returns ``replace_value`` otherwise.

.. function:: dedupe(iterable)
    
    Returns a list of elements in ``iterable`` with all dupes removed. The order of the elements is preserved.

.. function:: flatten(iterables, start_with=None)
    
    Takes the list of iterable ``iterables`` and returns a list containing elements of every iterable.
    
    If ``start_with`` is not None, the result will start with ``start_with`` items, exactly as if ``start_with`` would be the first item of lists.

.. function:: first(iterable)
    
    Returns the first item of ``iterable`` or ``None`` if empty.

.. function:: tryint(value, default=0)
    
    Tries to convert ``value`` to in ``int`` and returns ``default`` if it fails.

.. function:: escape(s, to_escape, escape_with='\\')
    
    Returns ``s`` with characters in ``to_escape`` all prepended with ``escape_with``.

.. function:: format_size(size, decimal=0, forcepower=-1, showdesc=True)
    
    Transform a byte count ``size`` in a formatted string (KB, MB etc..). ``decimal`` is the number digits after the dot. ``forcepower`` is the desired suffix. 0 is B, 1 is KB, 2 is MB etc.. if kept at -1, the suffix will be automatically chosen (so the resulting number is always below 1024). If ``showdesc`` is True, the suffix will be shown after the number. Usage example::
    
        >>> format_size(1234, decimal=2, showdesc=True)
        '1.21 KB'

.. function:: format_time(seconds, with_hours=True)
    
    Transforms seconds in a hh:mm:ss string.
    
    If `with_hours` if false, the format is mm:ss.

.. function:: format_time_decimal(seconds)

    Transforms seconds in a strings like '3.4 minutes'.

.. function:: get_file_ext(filename)
    
    Returns the lowercase extension part of ``filename``, without the dot.

.. function:: pluralize(number, word, decimals=0, plural_word=None)
    
    Returns a string with ``number`` in front of ``word``, and adds a 's' to ``word`` if ``number`` > 1. If ``plural_word`` is defined, it will replace ``word`` in plural cases instead of appending a 's'.

.. function:: rem_file_ext(filename)
    
    Returns ``filename`` without extension.

.. function:: multi_replace(s, replace_from, replace_to='')
    
    A function like str.replace() with multiple replacements. ``replace_from`` is a list of things you want to replace (Ex: ``['a','bc','d']``). ``replace_to`` is a list of what you want to replace to. If ``replace_to`` is a list and has the same length as ``replace_from``, ``replace_from`` items will be translated to corresponding ``replace_to``. A ``replace_to`` list must have the same length as ``replace_from``. If ``replace_to`` is a string, all ``replace_from`` occurences will be replaced by that string. ``replace_from`` can also be a string. If it is, every char in it will be translated as if ``replace_from`` would be a list of chars. If ``replace_to`` is a string and has the same length as ``replace_from``, it will be transformed into a list.
    
.. function:: open_if_filename(infile, mode='rb')

    If ``infile`` is a string, it opens and returns it. If it's already a file object, it simply returns it. This function returns ``(file, should_close_flag)``. The should_close_flag is True is a file has effectively been opened (if we already pass a file object, we assume that the responsibility for closing the file has already been taken). Example usage::
    
        fp, shouldclose = open_if_filename(infile)
        dostuff()
        if shouldclose:
            fp.close()
    
.. class:: FileOrPath(file_or_path, mode='rb')

    Does the same as :func:`open_if_filename`, but it can be used with a ``with`` statement. Example::
    
        with FileOrPath(infile):
            dostuff()

.. function:: delete_if_empty(path, files_to_delete=[])

    Same as with :func:`clean_empty_dirs`, but not recursive.

.. function:: modified_after(first_path, second_path)

    Returns True if ``first_path``'s mtime is higher than ``second_path``'s mtime.