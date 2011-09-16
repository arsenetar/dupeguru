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
    NSTableColumn *refCol = [matches tableColumnWithIdentifier:@"0"];
    _resultColumns = [[NSMutableArray alloc] init];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"0"]]; // File Name
    [_resultColumns addObject:[self getColumnForIdentifier:1 title:TRCOL(@"Folder") width:120 refCol:refCol]];
    NSTableColumn *sizeCol = [self getColumnForIdentifier:2 title:TRCOL(@"Size (KB)") width:63 refCol:refCol];
    [[sizeCol dataCell] setAlignment:NSRightTextAlignment];
    [_resultColumns addObject:sizeCol];
    [_resultColumns addObject:[self getColumnForIdentifier:3 title:TRCOL(@"Kind") width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:4 title:TRCOL(@"Dimensions") width:80 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:5 title:TRCOL(@"Modification") width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:6 title:TRCOL(@"Match %") width:58 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:7 title:TRCOL(@"Dupe Count") width:80 refCol:refCol]];
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

- (NSString *)getScanErrorMessageForCode:(NSInteger)errorCode
{
    if (errorCode == 4) {
        return TR(@"IPhotoAppNotFoundMsg");
    }
    return [super getScanErrorMessageForCode:errorCode];
}

/* Actions */
- (IBAction)clearPictureCache:(id)sender
{
    NSString *msg = TR(@"ClearPictureCacheConfirmMsg");
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
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
    [columnsOrder addObject:@"6"];
    NSMutableDictionary *columnsWidth = [NSMutableDictionary dictionary];
    [columnsWidth setObject:i2n(162) forKey:@"0"];
    [columnsWidth setObject:i2n(142) forKey:@"1"];
    [columnsWidth setObject:i2n(63) forKey:@"2"];
    [columnsWidth setObject:i2n(73) forKey:@"4"];
    [columnsWidth setObject:i2n(58) forKey:@"6"];
    [self restoreColumnsPosition:columnsOrder widths:columnsWidth];
}
@end