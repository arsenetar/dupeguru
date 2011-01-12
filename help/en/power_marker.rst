Power Marker
============

You will probably not use the Power Marker feature very often, but if you get into a situation where you need it, you will be pretty happy that this feature exists.

What is it?
-----------

When the Power Marker mode is enabled, the duplicates are shown without their respective reference file. You can select, mark and sort this list, just like in normal mode.

So, what is it for?
-------------------

The dupeGuru results, when in normal mode, are sorted according to duplicate groups' **reference file**. This means that if you want, for example, to mark all duplicates with the "exe" extension, you cannot just sort the results by "Kind" to have all exe duplicates together because a group can be composed of more than one kind of files. That is where Power Marker comes into play. To mark all your "exe" duplicates, you just have to:

* Enable the Power marker mode.
* Add the "Kind" column with the "Columns" menu.
* Click on that "Kind" column to sort the list by kind.
* Locate the first duplicate with a "exe" kind.
* Select it.
* Scroll down the list to locate the last duplicate with a "exe" kind.
* Hold Shift and click on it.
* Press Space to mark all selected duplicates.

Power Marker and delta values
-----------------------------

The Power Marker unveil its true power when you use it with the **Delta Values** switch turned on. When you turn it on, relative values will be displayed instead of absolute ones. So if, for example, you want to remove from your results all duplicates that are more than 300 KB away from their reference, you could sort the Power Marker by Size, select all duplicates under -300 in the Size column, delete them, and then do the same for duplicates over 300 at the bottom of the list.

You could also use it to change the reference priority of your duplicate list. When you make a fresh scan, if there are no reference directories, the reference file of every group is the biggest file. If you want to change that, for example, to the latest modification time, you can sort the Power Marker by modification time in **descending** order, select all duplicates with a modification time delta value higher than 0 and click on **Make Selected Reference**. The reason why you must make the sort order descending is because if 2 files among the same duplicate group are selected when you click on **Make Selected Reference**, only the first of the list will be made reference, the other will be ignored. And since you want the last modified file to be reference, having the sort order descending assures you that the first item of the list will be the last modified.

