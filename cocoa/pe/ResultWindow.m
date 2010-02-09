/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "ResultWindow.h"
#import "Dialogs.h"
#import "ProgressController.h"
#import "RegistrationInterface.h"
#import "Utils.h"
#import "AppDelegate.h"
#import "Consts.h"

@implementation ResultWindow
/* Override */
- (void)awakeFromNib
{
    [super awakeFromNib];
    [[self window] setTitle:@"dupeGuru Picture Edition"];
    _deltaColumns = [[NSMutableIndexSet indexSetWithIndexesInRange:NSMakeRange(2,5)] retain];
    [_deltaColumns removeIndex:3];
    [_deltaColumns removeIndex:4];
}

/* Actions */
- (IBAction)clearPictureCache:(id)sender
{
    if ([Dialogs askYesNo:@"Do you really want to remove all your cached picture analysis?"] == NSAlertSecondButtonReturn) // NO
        return;
    [(PyDupeGuru *)py clearPictureCache];
}

- (IBAction)resetColumnsToDefault:(id)sender
{
    NSMutableArray *columnsOrder = [NSMutableArray array];
    [columnsOrder addObject:@"0"];
    [columnsOrder addObject:@"1"];
    [columnsOrder addObject:@"2"];
    [columnsOrder addObject:@"4"];
    [columnsOrder addObject:@"7"];
    NSMutableDictionary *columnsWidth = [NSMutableDictionary dictionary];
    [columnsWidth setObject:i2n(121) forKey:@"0"];
    [columnsWidth setObject:i2n(120) forKey:@"1"];
    [columnsWidth setObject:i2n(63) forKey:@"2"];
    [columnsWidth setObject:i2n(73) forKey:@"4"];
    [columnsWidth setObject:i2n(58) forKey:@"7"];
    [self restoreColumnsPosition:columnsOrder widths:columnsWidth];
}

- (IBAction)startDuplicateScan:(id)sender
{
    if ([matches numberOfRows] > 0)
    {
        if ([Dialogs askYesNo:@"Are you sure you want to start a new duplicate scan?"] == NSAlertSecondButtonReturn) // NO
            return;
    }
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    PyDupeGuru *_py = (PyDupeGuru *)py;
    [_py setMinMatchPercentage:[ud objectForKey:@"minMatchPercentage"]];
    [_py setMixFileKind:[ud objectForKey:@"mixFileKind"]];
    [_py setMatchScaled:[ud objectForKey:@"matchScaled"]];
    int r = n2i([py doScan]);
    [matches reloadData];
    [self refreshStats];
    if (r != 0)
        [[ProgressController mainProgressController] hide];
    if (r == 1)
        [Dialogs showMessage:@"You cannot make a duplicate scan with only reference directories."];
    if (r == 3)
    {
        [Dialogs showMessage:@"The selected directories contain no scannable file."];
        [app toggleDirectories:nil];
    }
}

- (IBAction)toggleDirectories:(id)sender
{
    [(AppDelegate *)app toggleDirectories:sender];
}

/* Public */
- (void)initResultColumns
{
    NSTableColumn *refCol = [matches tableColumnWithIdentifier:@"0"];
    _resultColumns = [[NSMutableArray alloc] init];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"0"]]; // File Name
    [_resultColumns addObject:[self getColumnForIdentifier:1 title:@"Directory" width:120 refCol:refCol]];
    NSTableColumn *sizeCol = [self getColumnForIdentifier:2 title:@"Size (KB)" width:63 refCol:refCol];
    [[sizeCol dataCell] setAlignment:NSRightTextAlignment];
    [_resultColumns addObject:sizeCol];
    [_resultColumns addObject:[self getColumnForIdentifier:3 title:@"Kind" width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:4 title:@"Dimensions" width:80 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:5 title:@"Creation" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:6 title:@"Modification" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:7 title:@"Match %" width:58 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:8 title:@"Dupe Count" width:80 refCol:refCol]];
}
@end