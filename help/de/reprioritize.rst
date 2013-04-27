Re-Prioritizing duplicates
==========================

dupeGuru tries to automatically determine which duplicate should go in each group's reference
position, but sometimes it gets it wrong. In many cases, clever dupe sorting with "Delta Values"
and "Dupes Only" options in addition to the "Make Selected into Reference" action does the trick, but
sometimes, a more powerful option is needed. This is where the Re-Prioritization dialog comes into
play. You can summon it through the "Re-Prioritize Results" item in the "Actions" menu.

This dialog allows you to select criteria according to which a reference dupe will be selected in
each dupe group. The list of available criteria is on the left and the list of criteria you've
selected is on the right.

A criteria is a category followed by an argument. For example, "Size (Highest)" means that the dupe
with the biggest size will win. "Folder (/foo/bar)" means that dupes in this folder will win. To add
a criterion to the rightmost list, first select a category in the combobox, then select a
subargument in the list below, and then click on the right pointing arrow button.

The order of the list on the right is important (you can re-order items through drag & drop). When
picking a dupe for reference position, the first criterion is used. If there's a tie, the second
criterion is used and so on and so on. For example, if your arguments are "Size (Highest)" and then
"Filename (Doesn't end with a number)", the reference file that will be picked in a group will be
the biggest file, and if two or more files have the same size, the one that has a filename that
doesn't end with a number will be used. When all criteria result in ties, the order in which dupes
previously were in the group will be used.