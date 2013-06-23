==========================================
:mod:`build` - Build utilities for HS apps
==========================================

This module is a collection of function to help in HS apps build process.

.. function:: print_and_do(cmd)

    Prints ``cmd`` and executes it in the shell.

.. function:: build_all_qt_ui(base_dir='.')

    Calls Qt's ``pyuic4`` for each file in ``base_dir`` with a ".ui" extension. The resulting file is saved under ``{base_name}_ui.py``.

.. function:: build_dmg(app_path, dest_path)

    Builds a DMG volume with application at ``app_path`` and puts it in ``dest_path``. The name of the resulting DMG volume is determined by the app's name and version.

.. function:: add_to_pythonpath(path)

    Adds ``path`` to both ``PYTHONPATH`` env variable and ``sys.path``.

.. function:: copy_packages(packages_names, dest)

    Copy python packages ``packages_names`` to ``dest``, but without tests, testdata, mercurial data or C extension module source with it. ``py2app`` include and exclude rules are **quite** funky, and doing this is the only reliable way to make sure we don;t end up with useless stuff in our app.