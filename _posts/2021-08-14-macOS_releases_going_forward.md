---
title: "macOS Releases Going Forward"
---
We now have working macOS versions of dupeGuru built with both UI toolkits and supporting both 
Intel and M1 chips.  The latest downloads are as follows (see details below for more information):
- Qt Version [https://github.com/arsenetar/dupeguru/releases/download/4.1.1/dupeguru_macOS_Qt_4.1.1.zip](https://github.com/arsenetar/dupeguru/releases/download/4.1.1/dupeguru_macOS_Qt_4.1.1.zip)
- Cocoa Version [https://github.com/arsenetar/dupeguru/releases/download/4.1.1/dupeguru_macOS_Cocoa_4.1.1.dmg](https://github.com/arsenetar/dupeguru/releases/download/4.1.1/dupeguru_macOS_Cocoa_4.1.1.dmg)

## History
Awhile back we had detailed the state of issues with macOS versions in [macOS Version Notes]({% post_url 2021-03-09-macOS_version_notes %}).  We have now been able to package both Qt and Cocoa versions successfully for distribution.  
These versions are also compatible with Intel and M1 chips.  The Qt version had previously 
been held up due to issues with the packaging tools.  All the issues with packaging are now
resolved.

## Going Forward
Of the two versions, the Cocoa version can be considered the legacy version, due to needing 
to maintain a second UI layer.  We are considering phasing out the Cocoa version in future 
releases.  The Cocoa UI is already a ways behind the Qt version and does not implement several 
features.  There is no real development support for the Cocoa UI aside from minor bug fixes. 
As such we recommend users to start trying the Qt Version out and report any issues or missing 
items versus the Cocoa version.  The Cocoa UI will most likely not get any new features moving 
forward at this time, however we will try to support the current functionality until it is phased
out.

If there is interest in contributing to the development of the Cocoa UI, and helping provide support
for it, then we can consider not phasing it out.
