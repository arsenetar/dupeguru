Folder Selection
================

The first window you see when you launch dupeGuru is the folder selection window. This windows contains the list of the directories that will be scanned when you click on **Scan**.

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
