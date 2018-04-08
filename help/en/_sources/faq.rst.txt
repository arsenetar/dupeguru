Frequently Asked Questions
==========================

.. contents::

What is dupeGuru?
-----------------

dupeGuru is a tool to find duplicate files on your computer. It has three operational modes:
Standard, Music and Picture. Each mode has its own specialized preferences.

Each mode has multiple scan types, such as filename, contents, tags. Some scan types feature
advanced fuzzy matching algorithm, allowing you to find duplicates that other more rigid duplicate
scanners can't.

What makes it special?
----------------------

It's mostly about customizability. There's a lot of scanning options that allow you to get the
type of results you're really looking for.

How safe is it to use dupeGuru?
-------------------------------

Very safe. dupeGuru has been designed to make sure you don't delete files you didn't mean to delete.
First, there is the reference folder system that lets you define folders where you absolutely
**don't** want dupeGuru to let you delete files there, and then there is the group reference system
that makes sure that you will **always** keep at least one member of the duplicate group.

How can I report a bug a suggest a feature?
-------------------------------------------

dupeGuru is hosted on `Github`_ and it's also where issues are tracked. The best way to report a
bug or suggest a feature is to sign up on Github and `open an issue`_. 

The mark box of a file I want to delete is disabled. What must I do?
--------------------------------------------------------------------

You cannot mark the reference (The first file) of a duplicate group. However, what you can do is to
promote a duplicate file to reference. Thus, if a file you want to mark is reference, select a
duplicate file in the group that you want to promote to reference, and click on
**Actions-->Make Selected into Reference**. If the reference file is from a reference folder
(filename written in blue letters), you cannot remove it from the reference position.

I have a folder from which I really don't want to delete files.
---------------------------------------------------------------

If you want to be sure that dupeGuru will never delete file from a particular folder, make sure to
set its state to **Reference** at :doc:`folders`.

What is this '(X discarded)' notice in the status bar?
------------------------------------------------------

In some cases, some matches are not included in the final results for security reasons. Let me use
an example. We have 3 file: A, B and C. We scan them using a low filter hardness. The scanner
determines that A matches with B, A matches with C, but B does **not** match with C. Here, dupeGuru
has kind of a problem. It cannot create a duplicate group with A, B and C in it because not all
files in the group would match together. It could create 2 groups: one A-B group and then one A-C
group, but it will not, for security reasons. Lets think about it: If B doesn't match with C, it
probably means that either B, C or both are not actually duplicates. If there would be 2 groups (A-B
and A-C), you would end up delete both B and C. And if one of them is not a duplicate, that is
really not what you want to do, right? So what dupeGuru does in a case like this is to discard the
A-C match (and adds a notice in the status bar). Thus, if you delete B and re-run a scan, you will
have a A-C match in your next results.

I want to mark all files from a specific folder. What can I do?
---------------------------------------------------------------

Enable the :doc:`Dupes Only <results>` mode and click on the Folder column to sort your duplicates
by folder. It will then be easy for you to select all duplicates from the same folder, and then
press Space to mark all selected duplicates.

I want to remove all files that are more than 300 KB away from their reference file. What can I do?
---------------------------------------------------------------------------------------------------

* Enable the :doc:`Dupes Only <results>` mode.
* Enable the **Delta Values** mode.
* Click on the "Size" column to sort the results by size.
* Select all duplicates below -300.
* Click on **Remove Selected from Results**.
* Select all duplicates over 300.
* Click on **Remove Selected from Results**.

I want to make my latest modified files reference files. What can I do?
-----------------------------------------------------------------------

* Enable the :doc:`Dupes Only <results>` mode.
* Enable the **Delta Values** mode.
* Click on the "Modification" column to sort the results by modification date.
* Click on the "Modification" column again to reverse the sort order.
* Select all duplicates over 0.
* Click on **Make Selected into Reference**.

I want to mark all duplicates containing the word "copy". How do I do that?
---------------------------------------------------------------------------

* Type "copy" in the "Filter" field in the top-right corner of the result window.
* Click on **Mark --> Mark All**.

I want to remove all songs that are more than 3 seconds away from their reference file. What can I do?
------------------------------------------------------------------------------------------------------

* Enable the :doc:`Dupes Only <results>` mode.
* Enable the **Delta Values** mode.
* Click on the "Time" column to sort the results by time.
* Select all duplicates below -00:03.
* Click on **Remove Selected from Results**.
* Select all duplicates over 00:03.
* Click on **Remove Selected from Results**.

I want to make my highest bitrate songs reference files. What can I do?
-----------------------------------------------------------------------

* Enable the :doc:`Dupes Only <results>` mode.
* Enable the **Delta Values** mode.
* Click on the "Bitrate" column to sort the results by bitrate.
* Click on the "Bitrate" column again to reverse the sort order.
* Select all duplicates over 0.
* Click on **Make Selected into Reference**.

I don't want [live] and [remix] versions of my songs counted as duplicates. How do I do that?
---------------------------------------------------------------------------------------------

If your comparison threshold is low enough, you will probably end up with live and remix
versions of your songs in your results. There's nothing you can do to prevent that, but there's
something you can do to easily remove them from your results after the scan: post-scan
filtering. If, for example, you want to remove every song with anything inside square brackets
[]:

* Type "[*]" in the "Filter" field in the top-right corner of the result window.
* Click on **Mark --> Mark All**.
* Click on **Actions --> Remove Selected from Results**.

The "Filter Hardness" slider in the preferences won't move!
-----------------------------------------------------------

This slider is only relevant for scan types that support "fuzziness". Many scan types, such as the
"Contents" type, only support exact matches. When these types are selected, the slider is disabled.

On some OS, the fact that it's disabled is harder to see than on others, but if you can't move the
slider, it means that this preference is irrelevant in your current scan type.

I've tried to send my duplicates to Trash, but dupeGuru is telling me it can't do it. Why? What can I do?
---------------------------------------------------------------------------------------------------------

Most of the time, the reason why dupeGuru can't send files to Trash is because of file permissions.
You need *write* permissions on files you want to send to Trash.

If dupeGuru still gives you troubles after fixing your permissions, try enabling the "Directly
delete files" option that is offered to you when you activate Send to Trash. This will not send
files to the Trash, but delete them immediately. In some cases, for example on network storage
(NAS), this has been known to work when normal deletion didn't.

If this fail, `HS forums`_ might be of some help.

Why is Picture mode's contents scan so slow?
--------------------------------------------

This scanning method is very different from methods. It can detect duplicate photos even if they
are not exactly the same. This very cool capability has a cost: time. Every picture has to be
individually and fuzzily matched to all others, and this takes a lot of CPU power.

If all you need to find is exact duplicates, just use the standard mode of dupeGuru with the
Contents scan method. If your photos have EXIF tags, you can also try the "EXIF" scan method which
is much faster.

Where are user files located?
-----------------------------

For some reason, you'd like to remove or edit dupeGuru's user files (debug logs, caches, etc.).
Where they're located depends on your platform:

* Linux: ``~/.local/share/data/Hardcoded Software/dupeGuru``
* Mac OS X: ``~/Library/Application Support/dupeGuru``

Preferences are stored elsewhere:

* Linux: ``~/.config/Hardcoded Software/dupeGuru.conf``
* Mac OS X: In the built-in ``defaults`` system, as ``com.hardcoded-software.dupeguru``

.. _HS forums: https://forum.hardcoded.net/
.. _Github: https://github.com/hsoft/dupeguru
.. _open an issue: https://github.com/hsoft/dupeguru/wiki/issue-labels

