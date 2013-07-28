Results
=======

When dupeGuru is finished scanning for duplicates, it will show its results in the form of duplicate group list.

About duplicate groups
----------------------

A duplicate group is a group of files that all match together. Every group has a **reference file** and one or more **duplicate files**. The reference file is the first file of the group. Its mark box is disabled. Below it, and indented, are the duplicate files.

You can mark duplicate files, but you can never mark the reference file of a group. This is a security measure to prevent dupeGuru from deleting not only duplicate files, but their reference. You sure don't want that, do you?

What determines which files are reference and which files are duplicates is first their folder state. A file from a reference folder will always be reference in a duplicate group. If all files are from a normal folder, the size determine which file will be the reference of a duplicate group. dupeGuru assumes that you always want to keep the biggest file, so the biggest files will take the reference position.

You can change the reference file of a group manually. To do so, select the duplicate file you want
to promote to reference, and click on **Actions-->Make Selected into Reference**.

Reviewing results
-----------------

Although you can just click on **Edit-->Mark All** and then **Actions-->Send Marked to Recycle bin** to quickly delete all duplicate files in your results, it is always recommended to review all duplicates before deleting them.

To help you reviewing the results, you can bring up the **Details panel**. This panel shows all the details of the currently selected file as well as its reference's details. This is very handy to quickly determine if a duplicate really is a duplicate. You can also double-click on a file to open it with its associated application.

If you have more false duplicates than true duplicates (If your filter hardness is very low), the best way to proceed would be to review duplicates, mark true duplicates and then click on **Actions-->Send Marked to Recycle bin**. If you have more true duplicates than false duplicates, you can instead mark all files that are false duplicates, and use **Actions-->Remove Marked from Results**.

Marking and Selecting
---------------------

A **marked** duplicate is a duplicate with the little box next to it having a check-mark. A **selected** duplicate is a duplicate being highlighted. The multiple selection actions can be performed in dupeGuru in the standard way (Shift/Command/Control click). You can toggle all selected duplicates' mark state by pressing **space**.

Show Dupes Only
---------------

When this mode is enabled, the duplicates are shown without their respective reference file. You can select, mark and sort this list, just like in normal mode.

The dupeGuru results, when in normal mode, are sorted according to duplicate groups' **reference file**. This means that if you want, for example, to mark all duplicates with the "exe" extension, you cannot just sort the results by "Kind" to have all exe duplicates together because a group can be composed of more than one kind of files. That is where Dupes Only mode comes into play. To mark all your "exe" duplicates, you just have to:

* Enable the Dupes Only mode.
* Add the "Kind" column with the "Columns" menu.
* Click on that "Kind" column to sort the list by kind.
* Locate the first duplicate with a "exe" kind.
* Select it.
* Scroll down the list to locate the last duplicate with a "exe" kind.
* Hold Shift and click on it.
* Press Space to mark all selected duplicates.

Delta Values
------------

If you turn this switch on, numerical columns will display the value relative to the duplicate's
reference instead of the absolute values. These delta values will also be displayed in a different
color, orange,  so you can spot them easily. For example, if a duplicate is 1.2 MB and its reference
is 1.4 MB, the Size column will display -0.2 MB.

Moreover, non-numerical values will also be in orange if their value is different from their
reference, and stay black if their value is the same. Combined with column sorting in Dupes Only
mode, this allows for very powerful post-scan filtering.

Dupes Only and Delta Values
---------------------------

The Dupes Only mode unveil its true power when you use it with the Delta Values switch turned on.
When you turn it on, relative values will be displayed instead of absolute ones. So if, for example,
you want to remove from your results all duplicates that are more than 300 KB away from their
reference, you could sort the dupes only results by Size, select all duplicates under -300 in the
Size column, delete them, and then do the same for duplicates over 300 at the bottom of the list.

Same thing for non-numerical values: When Dupes Only and Delta Values are enabled at the same time,
column sorting groups rows depending on whether they're orange or not. Example: You ran a contents
scan, but you would only like to delete duplicates that have the same filename? Sort by filename
and all dupes with their filename attribute being the same as the reference will be grouped
together, their value being in black.

You could also use it to change the reference priority of your duplicate list. When you make a fresh
scan, if there are no reference folders, the reference file of every group is the biggest file. If
you want to change that, for example, to the latest modification time, you can sort the dupes only
results by modification time in **descending** order, select all duplicates with a modification time
delta value higher than 0 and click on **Make Selected into Reference**. The reason why you must
make the sort order descending is because if 2 files among the same duplicate group are selected
when you click on **Make Selected into Reference**, only the first of the list will be made
reference, the other will be ignored. And since you want the last modified file to be reference,
having the sort order descending assures you that the first item of the list will be the last
modified.

Filtering
---------

dupeGuru supports post-scan filtering. With it, you can narrow down your results so you can perform actions on a subset of it. For example, you could easily mark all duplicates with their filename containing "copy" from your results using the filter.

**Windows:** To use the filtering feature, click on Actions --> Apply Filter, write down the filter you want to apply and click OK. To go back to unfiltered results, click on Actions --> Cancel Filter.

**Mac OS X:** To use the filtering feature, type your filter in the "Filter" search field in the toolbar. To go back to unfiltered result, blank out the field, or click on the "X".

In simple mode (the default mode), whatever you type as the filter is the string used to perform the actual filtering, with the exception of one wildcard: **\***. Thus, if you type "[*]" as your filter, it will match anything with [] brackets in it, whatever is in between those brackets.

For more advanced filtering, you can turn "Use regular expressions when filtering" on. The filtering feature will then use **regular expressions**. A regular expression is a language for matching text. Explaining them is beyond the scope of this document. A good place to start learning it is `regular-expressions.info <http://www.regular-expressions.info>`_.

Matches are case insensitive in both simple and regexp mode.

For the filter to match, your regular expression don't have to match the whole filename, it just have to contain a string matching the expression.

You might notice that not all duplicates in the filtered results will match your filter. That is because as soon as one single duplicate in a group matches the filter, the whole group stays in the results so you can have a better view of the duplicate's context. However, non-matching duplicates are in "reference mode". Therefore, you can perform actions like Mark All and be sure to only mark filtered duplicates.

Action Menu
-----------

* **Clear Ignore List:** Remove all ignored matches you added. You have to start a new scan for the
  newly cleared ignore list to be effective.
* **Export Results to XHTML:** Take the current results, and create an XHTML file out of it. The
  columns that are visible when you click on this button will be the columns present in the XHTML
  file. The file will automatically be opened in your default browser.
* **Send Marked to Trash:** Send all marked duplicates to trash, obviously. Before proceeding,
  you'll be presented deletion options (see below).
* **Move Marked to...:** Prompt you for a destination, and then move all marked files to that
  destination. Source file's path might be re-created in destination, depending on the
  "Copy and Move" preference.
* **Copy Marked to...:** Prompt you for a destination, and then copy all marked files to that
  destination. Source file's path might be re-created in destination, depending on the
  "Copy and Move" preference.
* **Remove Marked from Results:** Remove all marked duplicates from results. The actual files will
  not be touched and will stay where they are.
* **Remove Selected from Results:** Remove all selected duplicates from results. Note that all
  selected reference files will be ignored, only duplicates can be removed with this action.
* **Make Selected into Reference:** Promote all selected duplicates to reference. If a duplicate is
  a part of a group having a reference file coming from a reference folder (in blue color), no
  action will be taken for this duplicate. If more than one duplicate among the same group are
  selected, only the first of each group will be promoted.
* **Add Selected to Ignore List:** This first removes all selected duplicates from results, and
  then add the match of that duplicate and the current reference in the ignore list. This match
  will not come up again in further scan. The duplicate itself might come back, but it will be
  matched with another reference file. You can clear the ignore list with the Clear Ignore List
  command.
* **Open Selected with Default Application:** Open the file with the application associated with
  selected file's type.
* **Reveal Selected in Finder:** Open the folder containing selected file.
* **Invoke Custom Command:** Invokes the external application you've set up in your preferences
  using the current selection as arguments in the invocation.
* **Rename Selected:** Prompts you for a new name, and then rename the selected file.

**Warning about moving files in iPhoto/iTunes:** When using the "Move Marked" action on duplicates 
that come from iPhoto or iTunes, files are copied, not moved. dupeGuru cannot use the Move action
on those files.

Deletion Options
----------------

These options affect how duplicate deletion takes place. Most of the time, you don't need to enable
any of them.

* **Link deleted files:** The deleted files are replaced by a link to the reference file. You have
  a choice of replacing it either with a `symlink`_ or a `hardlink`_. It's better to read the whole
  wikipedia pages about them to make a informed choice, but in short, a symlink is a shortcut to
  the file's path. If the original file is deleted or moved, the link is broken. A hardlink is a
  link to the file *itself*. That link is as good as a "real" file. Only when *all* hardlinks to a
  file are deleted is the file itself deleted.
  
  On OSX and Linux, this feature is supported fully, but under Windows, it's a bit complicated.
  Windows XP doesn't support it, but Vista and up support it. However, for the feature to work,
  dupeGuru has to run with administrative privileges.

* **Directly delete files:** Instead of sending files to trash, directly delete them. This is used
  for troubleshooting and you normally don't need to enable this unless dupeGuru has problems
  deleting files normally, something that can happens when you try to delete files on network
  storage (NAS).

.. _hardlink: http://en.wikipedia.org/wiki/Hard_link
.. _symlink: http://en.wikipedia.org/wiki/Symbolic_link