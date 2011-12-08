/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ResultWindow.h"
#import "Dialogs.h"
#import "Utils.h"
#import "Consts.h"
#import "PyDupeGuru.h"

@implementation ResultWindow
/* Override */
- (void)initResultColumns
{
    HSColumnDef defs[] = {
        {@"marked", 26, 26, 26, NO, [NSButtonCell class]},
        {@"name", 162, 16, 0, YES, nil},
        {@"folder_path", 142, 16, 0, YES, nil},
        {@"size", 63, 16, 0, YES, nil},
        {@"extension", 40, 16, 0, YES, nil},
        {@"dimensions", 73, 16, 0, YES, nil},
        {@"mtime", 120, 16, 0, YES, nil},
        {@"percentage", 58, 16, 0, YES, nil},
        {@"dupe_count", 80, 16, 0, YES, nil},
        nil
    };
    [[table columns] initializeColumns:defs];
    NSTableColumn *c = [matches tableColumnWithIdentifier:@"marked"];
    [[c dataCell] setButtonType:NSSwitchButton];
    [[c dataCell] setControlSize:NSSmallControlSize];
    c = [matches tableColumnWithIdentifier:@"size"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[table columns] restoreColumns];
}

- (void)setScanOptions
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    PyDupeGuru *_py = (PyDupeGuru *)py;
    [_py setScanType:[ud objectForKey:@"scanType"]];
    [_py setMinMatchPercentage:[ud objectForKey:@"minMatchPercentage"]];
    [_py setMixFileKind:n2b([ud objectForKey:@"mixFileKind"])];
    [_py setIgnoreHardlinkMatches:n2b([ud objectForKey:@"ignoreHardlinkMatches"])];
    [_py setMatchScaled:[ud objectForKey:@"matchScaled"]];
}

/* Actions */
- (IBAction)clearPictureCache:(id)sender
{
    NSString *msg = TR(@"Do you really want to remove all your cached picture analysis?");
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [(PyDupeGuru *)py clearPictureCache];
}
@end