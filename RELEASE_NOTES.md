# dupeGuru 4.3.2 — bulk folder states

This release of the gunnerman1 fork adds bulk state editing to Folder Selection.

- Select folders with Ctrl-click or Shift-click, as in the duplicate results list.
- Open any selected folder's State dropdown to apply Normal, Reference, or Excluded to the selection.
- Keep selection and expansion while inherited states refresh, with one refresh per batch.
- Save and reload folder states using the existing directories file format.

For Albums: keep Albums Normal, expand it, select the artist folders only, and choose Reference.
Their deeper folders inherit Reference. If a selected parent changes state, its descendants follow
the existing inheritance rules; selected children receive the same chosen state deterministically.

Download the Windows 64-bit installer, or extract the portable ZIP and run dupeguru-win64.exe.
The portable ZIP includes the complete application folder; Python is not required.
This is an unsigned community fork build. SHA256SUMS.txt contains asset checksums.
