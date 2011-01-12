Directories
===========

There is a panel in dupeGuru called **Directories**. You can open it by clicking on the **Directories** button. This directory contains the list of the directories that will be scanned when you click on **Start Scanning**.

This panel is quite straightforward to use. If you want to add a directory, click on **Add**. If you added directories before, a popup menu with a list of recent directories you added will pop. You can click on one of them to add it directly to your list. If you click on the first item of the popup menu, **Add New Directory...**, you will be prompted for a directory to add. If you never added a directory, no menu will pop and you will directly be prompted for a new directory to add.

To remove a directory, select the directory to remove and click on **Remove**. If a subdirectory is selected when you click remove, the selected directory will be set to **excluded** state (see below) instead of being removed.

Directory states
----------------

Every directory can be in one of these 3 states:

* **Normal:** Duplicates found in these directories can be deleted.
* **Reference:** Duplicates found in this directory **cannot** be deleted. Files in reference directories will be in a blue color in the results.
* **Excluded:** Files in this directory will not be included in the scan.

The default state of a directory is, of course, **Normal**. You can use **Reference** state for a directory if you want to be sure that you won't delete any file from it.

When you set the state of a directory, all subdirectories of this directory automatically inherit this state unless you explicitly set a subdirectory's state.
