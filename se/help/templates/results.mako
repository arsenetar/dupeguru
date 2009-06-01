<%!
	title = 'Results'
	selected_menu_item = 'Results'
%>
<%inherit file="/base_dg.mako"/>

When dupeGuru is finished scanning for duplicates, it will show its results in the form of duplicate group list.

About duplicate groups
-----

A duplicate group is a group of files that all match together. Every group has a **reference file** and one or more **duplicate files**. The reference file is the first file of the group. Its mark box is disabled. Below it, and indented, are the duplicate files.

You can mark duplicate files, but you can never mark the reference file of a group. This is a security measure to prevent dupeGuru from deleting not only duplicate files, but their reference. You sure don't want that, do you?

What determines which files are reference and which files are duplicates is first their directory state. A files from a reference directory will always be reference in a duplicate group. If all files are from a normal directory, the size determine which file will be the reference of a duplicate group. dupeGuru assumes that you always want to keep the biggest file, so the biggest files will take the reference position.

You can change the reference file of a group manually. To do so, select the duplicate file you want to promote to reference, and click on **Actions-->Make Selected Reference**.

Reviewing results
-----

Although you can just click on **Edit-->Mark All** and then **Actions-->Send Marked to Recycle bin** to quickly delete all duplicate files in your results, it is always recommended to review all duplicates before deleting them.

To help you reviewing the results, you can bring up the **Details panel**. This panel shows all the details of the currently selected file as well as its reference's details. This is very handy to quickly determine if a duplicate really is a duplicate. You can also double-click on a file to open it with its associated application.

If you have more false duplicates than true duplicates (If your filter hardness is very low), the best way to proceed would be to review duplicates, mark true duplicates and then click on **Actions-->Send Marked to Recycle bin**. If you have more true duplicates than false duplicates, you can instead mark all files that are false duplicates, and use **Actions-->Remove Marked from Results**.

Marking and Selecting
-----

A **marked** duplicate is a duplicate with the little box next to it having a check-mark. A **selected** duplicate is a duplicate being highlighted. The multiple selection actions can be performed in dupeGuru in the standard way (Shift/Command/Control click). You can toggle all selected duplicates' mark state by pressing **space**.

Delta Values
-----

If you turn this switch on, some columns will display the value relative to the duplicate's reference instead of the absolute values. These delta values will also be displayed in a different color so you can spot them easily. For example, if a duplicate is 1.2 MB and its reference is 1.4 MB, the Size column will display -0.2 MB. This option is a killer feature when combined with the [Power Marker](power_marker.htm).

Filtering
-----

dupeGuru supports post-scan filtering. With it, you can narrow down your results so you can perform actions on a subset of it. For example, you could easily mark all duplicates with their filename containing "copy" from your results using the filter.

**Windows:** To use the filtering feature, click on Actions --> Apply Filter, write down the filter you want to apply and click OK. To go back to unfiltered results, click on Actions --> Cancel Filter.

**Mac OS X:** To use the filtering feature, type your filter in the "Filter" search field in the toolbar. To go back to unfiltered result, blank out the field, or click on the "X".

In simple mode (the default mode), whatever you type as the filter is the string used to perform the actual filtering, with the exception of one wildcard: **\***. Thus, if you type "[*]" as your filter, it will match anything with [] brackets in it, whatever is in between those brackets.

For more advanced filtering, you can turn "Use regular expressions when filtering" on. The filtering feature will then use **regular expressions**. A regular expression is a language for matching text. Explaining them is beyond the scope of this document. A good place to start learning it is <http://www.regular-expressions.info>.

Matches are case insensitive in both simple and regexp mode.

For the filter to match, your regular expression don't have to match the whole filename, it just have to contain a string matching the expression.

You might notice that not all duplicates in the filtered results will match your filter. That is because as soon as one single duplicate in a group matches the filter, the whole group stays in the results so you can have a better view of the duplicate's context. However, non-matching duplicates are in "reference mode". Therefore, you can perform actions like Mark All and be sure to only mark filtered duplicates.

Action Menu
-----

* **Start Duplicate Scan:** Starts a new duplicate scan.
* **Clear Ignore List:** Remove all ignored matches you added. You have to start a new scan for the newly cleared ignore list to be effective.
* **Export Results to XHTML:** Take the current results, and create an XHTML file out of it. The columns that are visible when you click on this button will be the columns present in the XHTML file. The file will automatically be opened in your default browser.
* **Send Marked to Trash:** Send all marked duplicates to trash, obviously.
* **Move Marked to...:** Prompt you for a destination, and then move all marked files to that destination. Source file's path might be re-created in destination, depending on the "Copy and Move" preference.
* **Copy Marked to...:** Prompt you for a destination, and then copy all marked files to that destination. Source file's path might be re-created in destination, depending on the "Copy and Move" preference.
* **Remove Marked from Results:** Remove all marked duplicates from results. The actual files will not be touched and will stay where they are.
* **Remove Selected from Results:** Remove all selected duplicates from results. Note that all selected reference files will be ignored, only duplicates can be removed with this action.
* **Make Selected Reference:** Promote all selected duplicates to reference. If a duplicate is a part of a group having a reference file coming from a reference directory (in blue color), no action will be taken for this duplicate. If more than one duplicate among the same group are selected, only the first of each group will be promoted.
* **Add Selected to Ignore List:** This first removes all selected duplicates from results, and then add the match of that duplicate and the current reference in the ignore list. This match will not come up again in further scan. The duplicate itself might come back, but it will be matched with another reference file. You can clear the ignore list with the Clear Ignore List command.
* **Open Selected with Default Application:** Open the file with the application associated with selected file's type.
* **Reveal Selected in Finder:** Open the folder containing selected file.
* **Rename Selected:** Prompts you for a new name, and then rename the selected file.
