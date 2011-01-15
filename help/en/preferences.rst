Preferences
===========

.. only:: edition_se

    **Scan Type:** This option determines what aspect of the files will be compared in the duplicate scan. If you select **Filename**, dupeGuru will compare every filenames word-by-word and, depending on the other settings below, it will determine if enough words are matching to consider 2 files duplicates. If you select **Content**, only files with the exact same content will match.
    
    **Filter Hardness:** If you chose the **Filename** scan type, this option determines how similar two filenames must be for dupeGuru to consider them duplicates. If the filter hardness is, for example 80, it means that 80% of the words of two filenames must match. To determine the matching percentage, dupeGuru first counts the total number of words in **both** filenames, then count the number of words matching (every word matching count as 2), and then divide the number of words matching by the total number of words. If the result is higher or equal to the filter hardness, we have a duplicate match. For example, "a b c d" and "c d e" have a matching percentage of 57 (4 words matching, 7 total words).

.. only:: edition_me

    **Scan Type:** This option determines what aspect of the files will be compared in the duplicate scan. The nature of the duplicate scan varies greatly depending on what you select for this option.

    * **Filename:** Every song will have its filename split into words, and then every word will be compared to compute a matching percentage. If this percentage is higher or equal to the **Filter Hardness** (see below for more details), dupeGuru will consider the 2 songs duplicates.
    * **Filename - Fields:** Like **Filename**, except that once filename have been split into words, these words are then grouped into fields. The field separator is " - ". The final matching percentage will be the lowest matching percentage among the fields. Thus, "An Artist - The Title" and "An Artist - Other Title" would have a matching percentage of 50 (With a **Filename** scan, it would be 75).
    * **Filename - Fields (No Order):** Like **Filename - Fields**, except that field order doesn't matter. For example, "An Artist - The Title" and "The Title - An Artist" would have a matching percentage of 100 instead of 0.
    * **Tags:** This method reads the tag (metadata) of every song and compare their fields. This method, like the **Filename - Fields**, considers the lowest matching field as its final matching percentage.
    * **Content:** This scan method use the actual content of the songs to determine which are duplicates. For 2 songs to match with this method, they must have the **exact same content**.
    * **Audio Content:** Same as content, but only the audio content is compared (without metadata).

    **Filter Hardness:** If you chose a filename or tag based scan type, this option determines how similar two filenames/tags must be for dupeGuru to consider them duplicates. If the filter hardness is, for example 80, it means that 80% of the words of two filenames must match. To determine the matching percentage, dupeGuru first counts the total number of words in **both** filenames, then count the number of words matching (every word matching count as 2), and then divide the number of words matching by the total number of words. If the result is higher or equal to the filter hardness, we have a duplicate match. For example, "a b c d" and "c d e" have a matching percentage of 57 (4 words matching, 7 total words).

    **Tags to scan:** When using the **Tags** scan type, you can select the tags that will be used for comparison.

.. only:: edition_se or edition_me

    **Word weighting:** If you chose the **Filename** scan type, this option slightly changes how matching percentage is calculated. With word weighting, instead of having a value of 1 in the duplicate count and total word count, every word have a value equal to the number of characters they have. With word weighting, "ab cde fghi" and "ab cde fghij" would have a matching percentage of 53% (19 total characters, 10 characters matching (4 for "ab" and 6 for "cde")).

    **Match similar words:** If you turn this option on, similar words will be counted as matches. For example "The White Stripes" and "The White Stripe" would have a match % of 100 instead of 66 with that option turned on. **Warning:** Use this option with caution. It is likely that you will get a lot of false positives in your results when turning it on. However, it will help you to find duplicates that you wouldn't have found otherwise. The scan process also is significantly slower with this option turned on.

.. only:: edition_pe

    **Filter Hardness:** The higher is this setting, the "harder" is the filter (In other words, the less results you get). Most pictures of the same quality match at 100% even if the format is different (PNG and JPG for example.). However, if you want to make a PNG match with a lower quality JPG, you will have to set the filer hardness to lower than 100. The default, 95, is a sweet spot.

    **Match scaled pictures together:** If you check this box, pictures of different dimensions will be allowed in the same duplicate group.

**Can mix file kind:** If you check this box, duplicate groups are allowed to have files with different extensions. If you don't check it, well, they aren't!

**Ignore duplicates hardlinking to the same file:** If this option is enabled, dupeGuru will verify duplicates to see if they refer to the same `inode <http://en.wikipedia.org/wiki/Inode>`_. If they do, they will not be considered duplicates. (Only for OS X and Linux)

**Use regular expressions when filtering:** If you check this box, the filtering feature will treat your filter query as a **regular expression**. Explaining them is beyond the scope of this document. A good place to start learning it is `regular-expressions.info <http://www.regular-expressions.info>`_.

**Remove empty folders after delete or move:** When this option is enabled, folders are deleted after a file is deleted or moved and the folder is empty.

**Copy and Move:** Determines how the Copy and Move operations (in the Action menu) will behave.

* **Right in destination:** All files will be sent directly in the selected destination, without trying to recreate the source path at all.
* **Recreate relative path:** The source file's path will be re-created in the destination folder up to the root selection in the Directories panel. For example, if you added ``/Users/foobar/SomeFolder`` to your Directories panel and you move ``/Users/foobar/SomeFolder/SubFolder/SomeFile.ext`` to the destination ``/Users/foobar/MyDestination``, the final destination for the file will be ``/Users/foobar/MyDestination/SubFolder`` (``SomeFolder`` has been trimmed from source's path in the final destination.).
* **Recreate absolute path:** The source file's path will be re-created in the destination folder in it's entirety. For example, if you move ``/Users/foobar/SomeFolder/SubFolder/SomeFile.ext`` to the destination ``/Users/foobar/MyDestination``, the final destination for the file will be ``/Users/foobar/MyDestination/Users/foobar/SomeFolder/SubFolder``.

In all cases, dupeGuru nicely handles naming conflicts by prepending a number to the destination filename if the filename already exists in the destination.

**Custom Command:** This preference determines the command that will be invoked by the "Invoke Custom Command" action. You can invoke any external application through this action. This can be useful if, for example, you have a nice diffing application installed.

The format of the command is the same as what you would write in the command line, except that there are 2 placeholders: **%d** and **%r**. These placeholders will be replaced by the path of the selected dupe (%d) and the path of the selected dupe's reference file (%r).
  
If the path to your executable contains space characters, you should enclose it in "" quotes. You should also enclose placeholders in quotes because it's very possible that paths to dupes and refs will contain spaces. Here's an example custom command::
  
    "C:\Program Files\SuperDiffProg\SuperDiffProg.exe" "%d" "%r"
