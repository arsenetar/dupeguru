<%!
	title = 'Preferences'
	selected_menu_item = 'Preferences'
%>
<%inherit file="/base_dg.mako"/>

**Filter Hardness:** The higher is this setting, the "harder" is the filter (In other words, the less results you get). Most pictures of the same quality match at 100% even if the format is different (PNG and JPG for example.). However, if you want to make a PNG match with a lower quality JPG, you will have to set the filer hardness to lower than 100. The default, 95, is a sweet spot.

**Match scaled pictures together:** If you check this box, pictures of different dimensions will be allowed in the same duplicate group.

**Can mix file kind:** If you check this box, duplicate groups are allowed to have files with different extensions. If you don't check it, well, they aren't!

**Use regular expressions when filtering:** If you check this box, the filtering feature will treat your filter query as a **regular expression**. Explaining them is beyond the scope of this document. A good place to start learning it is <http://www.regular-expressions.info>.

**Remove empty folders after delete or move:** When this option is enabled, folders are deleted after a file is deleted or moved and the folder is empty.

**Copy and Move:** Determines how the Copy and Move operations (in the Action menu) will behave.

* **Right in destination:** All files will be sent directly in the selected destination, without trying to recreate the source path at all.
* **Recreate relative path:** The source file's path will be re-created in the destination directory up to the root selection in the Directories panel. For example, if you added "/Users/foobar/Picture" to your Directories panel and you move "/Users/foobar/Picture/2006/06/photo.jpg" to the destination "/Users/foobar/MyDestination", the final destination for the file will be "/Users/foobar/MyDestination/2006/06" ("/Users/foobar/Picture" has been trimmed from source's path in the final destination.).
* **Recreate absolute path:** The source file's path will be re-created in the destination directory in it's entirety. For example, if you move "/Users/foobar/Picture/2006/06/photo.jpg" to the destination "/Users/foobar/MyDestination", the final destination for the file will be "/Users/foobar/MyDestination/Users/foobar/Picture/2006/06".

In all cases, dupeGuru PE nicely handles naming conflicts by prepending a number to the destination filename if the filename already exists in the destination.
