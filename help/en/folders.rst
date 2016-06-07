Folder Selection
================

The first window you see when you launch dupeGuru is the folder selection window. This windows
contains the basic input dupeGuru needs to start a scan:

* An Application Mode selection
* A Scan Type selection
* Folders to scan

Application Mode
----------------

dupeGuru had three main modes: Standard, Music and Picture.

Standard is for any type of files. This makes this mode the most polyvalent, but it lacks
specialized features other modes have.

Music mode scans only music files, but it supports tags comparison and its results window has many
audio-related informational columns.

Picture mode scans only pictures, but its contents scan type is a powerful fuzzy matcher that can
find pictures that are similar without being exactly the same.

Choosing an application mode not only changes available scan types in the selector below, but also
changes available options in the preferences panel. Thus, if you want to fine tune your scan, be
sure to open the preferences panel **after** you've selected the application mode.

Scan Type
---------

This selector determines the type of the scan we'll do. See :doc:`scan` for details about scan
types.

Folder List
-----------

To add a folder, click on the **+** button. If you added folder before, a popup
menu with a list of recent folders you added will pop. You can click on one of
them to add it directly to your list. If you click on the first item of the
popup menu, **Add New Folder...**, you will be prompted for a folder to add. If
you never added a folder, no menu will pop and you will directly be prompted
for a new folder to add.

An alternate way to add folders to the list is to drag them in the list.

To remove a folder, select the folder to remove and click on **-**. If a subfolder is selected when
you click the button, the selected folder will be set to **excluded** state (see below) instead of
being removed.

Folder states
-------------

Every folder can be in one of these 3 states:

**Normal:**
    Duplicates found in this folder can be deleted.
**Reference:**
    Duplicates found in this folder **cannot** be deleted. Files from this folder can
    only end up in **reference** position in the dupe group. If more than one file from reference
    folders end up in the same dupe group, only one will be kept. The others will be removed from
    the group.
**Excluded:**
    Files in this directory will not be included in the scan.

The default state of a folder is, of course, **Normal**. You can use **Reference** state for a
folder if you want to be sure that you won't delete any file from it.

When you set the state of a directory, all subfolders of this folder automatically inherit this
state unless you explicitly set a subfolder's state.

Scan
----

When you're ready, click on the **Scan** button to initiate the scanning process. When it's done,
you'll be shown the :doc:`results`.
