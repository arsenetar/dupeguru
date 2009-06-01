<%!
	title = 'dupeGuru F.A.Q.'
	selected_menu_item = 'F.A.Q.'
%>
<%inherit file="/base_dg.mako"/>

<%text filter="md">
### What is dupeGuru?

dupeGuru is a tool to find duplicate files on your computer. It can scan either filenames or content. The filename scan features a fuzzy matching algorithm that can find duplicate filenames even when they are not exactly the same.

### What makes it better than other duplicate scanners?

The scanning engine is extremely flexible. You can tweak it to really get the kind of results you want. You can read more about dupeGuru tweaking option at the [Preferences page](preferences.htm).

### How safe is it to use dupeGuru?

Very safe. dupeGuru has been designed to make sure you don't delete files you didn't mean to delete. First, there is the reference directory system that lets you define directories where you absolutely **don't** want dupeGuru to let you delete files there, and then there is the group reference system that makes sure that you will **always** keep at least one member of the duplicate group.

### What are the demo limitations of dupeGuru?

In demo mode, you can only perform actions (delete/copy/move) on 10 duplicates per session.

### The mark box of a file I want to delete is disabled. What must I do?

You cannot mark the reference (The first file) of a duplicate group. However, what you can do is to promote a duplicate file to reference. Thus, if a file you want to mark is reference, select a duplicate file in the group that you want to promote to reference, and click on **Actions-->Make Selected Reference**. If the reference file is from a reference directory (filename written in blue letters), you cannot remove it from the reference position.

### I have a directory from which I really don't want to delete files.

If you want to be sure that dupeGuru will never delete file from a particular directory, just open the **Directories panel**, select that directory, and set its state to **Reference**.

### What is this '(X discarded)' notice in the status bar?

In some cases, some matches are not included in the final results for security reasons. Let me use an example. We have 3 file: A, B and C. We scan them using a low filter hardness. The scanner determines that A matches with B, A matches with C, but B does **not** match with C. Here, dupeGuru has kind of a problem. It cannot create a duplicate group with A, B and C in it because not all files in the group would match together. It could create 2 groups: one A-B group and then one A-C group, but it will not, for security reasons. Lets think about it: If B doesn't match with C, it probably means that either B, C or both are not actually duplicates. If there would be 2 groups (A-B and A-C), you would end up delete both B and C. And if one of them is not a duplicate, that is really not what you want to do, right? So what dupeGuru does in a case like this is to discard the A-C match (and adds a notice in the status bar). Thus, if you delete B and re-run a scan, you will have a A-C match in your next results.

### I want to mark all files from a specific directory. What can I do?

Enable the [Power Marker](power_marker.htm) mode and click on the Directory column to sort your duplicates by Directory. It will then be easy for you to select all duplicates from the same directory, and then press Space to mark all selected duplicates.

### I want to remove all files that are more than 300 KB away from their reference file. What can I do?

* Enable the [Power Marker](power_marker.htm) mode.
* Enable the **Delta Values** mode.
* Click on the "Size" column to sort the results by size.
* Select all duplicates below -300.
* Click on **Remove Selected from Results**.
* Select all duplicates over 300.
* Click on **Remove Selected from Results**.

### I want to make my latest modified files reference files. What can I do?

* Enable the [Power Marker](power_marker.htm) mode.
* Enable the **Delta Values** mode.
* Click on the "Modification" column to sort the results by modification date.
* Click on the "Modification" column again to reverse the sort order (see Power Marker page to know why).
* Select all duplicates over 0.
* Click on **Make Selected Reference**.

### I want to mark all duplicates containing the word &quot;copy&quot;. How do I do that?

* **Windows**: Click on **Actions --> Apply Filter**, then type "copy", then click OK.
* **Mac OS X**: Type "copy" in the "Filter" field in the toolbar.
* Click on **Mark --> Mark All**.
</%text>