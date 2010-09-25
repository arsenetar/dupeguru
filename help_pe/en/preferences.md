**Filter Hardness:** The higher is this setting, the "harder" is the filter (In other words, the less results you get). Most pictures of the same quality match at 100% even if the format is different (PNG and JPG for example.). However, if you want to make a PNG match with a lower quality JPG, you will have to set the filer hardness to lower than 100. The default, 95, is a sweet spot.

**Match scaled pictures together:** If you check this box, pictures of different dimensions will be allowed in the same duplicate group.

**Can mix file kind:** If you check this box, duplicate groups are allowed to have files with different extensions. If you don't check it, well, they aren't!

**Ignore duplicates hardlinking to the same file:** If this option is enabled, dupeGuru will verify duplicates to see if they refer to the same [inode](http://en.wikipedia.org/wiki/Inode). If they do, they will not be considered duplicates. (Only for OS X and Linux)

**Use regular expressions when filtering:** If you check this box, the filtering feature will treat your filter query as a **regular expression**. Explaining them is beyond the scope of this document. A good place to start learning it is <http://www.regular-expressions.info>.

**Remove empty folders after delete or move:** When this option is enabled, folders are deleted after a file is deleted or moved and the folder is empty.

**Copy and Move:** Determines how the Copy and Move operations (in the Action menu) will behave.

* **Right in destination:** All files will be sent directly in the selected destination, without trying to recreate the source path at all.
* **Recreate relative path:** The source file's path will be re-created in the destination directory up to the root selection in the Directories panel. For example, if you added "/Users/foobar/Picture" to your Directories panel and you move "/Users/foobar/Picture/2006/06/photo.jpg" to the destination "/Users/foobar/MyDestination", the final destination for the file will be "/Users/foobar/MyDestination/2006/06" ("/Users/foobar/Picture" has been trimmed from source's path in the final destination.).
* **Recreate absolute path:** The source file's path will be re-created in the destination directory in it's entirety. For example, if you move "/Users/foobar/Picture/2006/06/photo.jpg" to the destination "/Users/foobar/MyDestination", the final destination for the file will be "/Users/foobar/MyDestination/Users/foobar/Picture/2006/06".

In all cases, dupeGuru PE nicely handles naming conflicts by prepending a number to the destination filename if the filename already exists in the destination.

**Custom Command:** This preference determines the command that will be invoked by the "Invoke Custom Command" action. You can invoke any external application through this action. This can be useful if, for example, you have a nice diffing application installed.

The format of the command is the same as what you would write in the command line, except that there are 2 placeholders: **%d** and **%r**. These placeholders will be replaced by the path of the selected dupe (%d) and the path of the selected dupe's reference file (%r).
  
If the path to your executable contains space characters, you should enclose it in "" quotes. You should also enclose placeholders in quotes because it's very possible that paths to dupes and refs will contain spaces. Here's an example custom command:
  
    "C:\Program Files\SuperDiffProg\SuperDiffProg.exe" "%d" "%r"
