Folder Selection
================

The first window you see when you launch dupeGuru is the folder selection window. This windows contains the list of the folders that will be scanned when you click on **Scan**.

This window is quite straightforward to use. If you want to add a folder, click on the **+** button. If you added folder before, a popup menu with a list of recent folders you added will pop. You can click on one of them to add it directly to your list. If you click on the first item of the popup menu, **Add New Folder...**, you will be prompted for a folder to add. If you never added a folder, no menu will pop and you will directly be prompted for a new folder to add.

An alternate way to add folders to the list is to drag them in the list.

To remove a folder, select the folder to remove and click on **-**. If a subfolder is selected when you click the button, the selected folder will be set to **excluded** state (see below) instead of being removed.

Folder states
-------------

Every folder can be in one of these 3 states:

* **Normal:** Duplicates found in this folder can be deleted.
* **Reference:** Duplicates found in this folder **cannot** be deleted. Files from this folder can only end up in **reference** position in the dupe group. If more than one file from reference folders end up in the same dupe group, only one will be kept. The others will be removed from the group.
* **Excluded:** Files in this directory will not be included in the scan.

The default state of a folder is, of course, **Normal**. You can use **Reference** state for a folder if you want to be sure that you won't delete any file from it.

When you set the state of a directory, all subfolders of this folder automatically inherit this state unless you explicitly set a subfolder's state.

.. only:: edition_pe

    iPhoto and Aperture libraries
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    
    dupeGuru PE supports iPhoto and Aperture, which means that it knows how to read these libraries
    and how to communicate with iPhoto and Aperture to remove photos from them. To use this feature,
    use the special "Add iPhoto Library" and "Add Aperture Library" buttons in the menu that pops
    up when you click the "+" button. This will then add a special folder for those libraries.
    
    When duplicates are deleted from an iPhoto library, it's sent to iPhoto's trash.
    
    When duplicates are deleted from an Aperture library, it unfortunately can't send it directly
    to trash, but it creates a special project called "dupeGuru Trash" in Aperture and send all
    photos in there. You can then send this project to the trash manually.

.. only:: edition_me

    iTunes library
    ^^^^^^^^^^^^^^
    
    dupeGuru ME supports iTunes, which means that it knows how to read its libraries and how to
    communicate with iTunes to remove songs from it. To use this feature, use the special
    "Add iTunes Library" button in the menu that pops up when you click the "+" button. This will
    then add a special folder for those libraries.
    
    When duplicates are deleted from an iTunes library, it's sent to the system trash, like a
    normal file, but it's also removed from iTunes, thus avoiding ending up with missing entries
    (entries with the "!" logo next to them).
