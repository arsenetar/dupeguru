===================================================
:mod:`conflict` - Detect and resolve name conflicts
===================================================

.. module:: conflict

When you have to deal with names that have to be unique and can conflict together, you can use this module that deals with conflicts by prepending unique numbers in ``[]`` brackets to the name.

.. function:: get_conflicted_name(other_names, name)

    Returns a name based on ``name`` that is guaranteed not to be in ``other_names``. Name conflicts are resolved by prepending numbers in ``[]`` brackets to the name.

.. function:: get_unconflicted_name(name)

    Returns ``name`` without ``[]`` brackets.

.. function:: is_conflicted(name)

    Returns whether ``name`` is prepended with a bracketed number.

.. function:: smart_copy(source_path, dest_path)

    Copies ``source_path`` to ``dest_path``, recursively. However, it does conflict resolution using functions in this module.

.. function:: smart_move(source_path, dest_path)

    Same as :func:`smart_copy`, but it moves files instead.
