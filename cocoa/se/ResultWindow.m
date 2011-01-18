/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ResultWindow.h"
#import "Utils.h"
#import "Consts.h"
#import "PyDupeGuru.h"

@implementation ResultWindow
/* Override */
- (id)initWithParentApp:(AppDelegateBase *)aApp;
{
    self = [super initWithParentApp:aApp];
    NSMutableIndexSet *deltaColumns = [NSMutableIndexSet indexSetWithIndex:2];
    [deltaColumns addIndex:4];
    [table setDeltaColumns:deltaColumns];
    return self;
}

- (void)initResultColumns
{
    NSTableColumn *refCol = [matches tableColumnWithIdentifier:@"0"];
    _resultColumns = [[NSMutableArray alloc] init];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"0"]]; // File Name
    [_resultColumns addObject:[self getColumnForIdentifier:1 title:TR(@"Folder") width:120 refCol:refCol]];
    NSTableColumn *sizeCol = [self getColumnForIdentifier:2 title:TR(@"Size (KB)") width:63 refCol:refCol];
    [[sizeCol dataCell] setAlignment:NSRightTextAlignment];
    [_resultColumns addObject:sizeCol];
    [_resultColumns addObject:[self getColumnForIdentifier:3 title:TR(@"Kind") width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:4 title:TR(@"Modification") width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:5 title:TR(@"Match %") width:60 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:6 title:TR(@"Words Used") width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:7 title:TR(@"Dupe Count") width:80 refCol:refCol]];
}

- (void)setScanOptions
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    PyDupeGuru *_py = (PyDupeGuru *)py;
    [_py setScanType:[ud objectForKey:@"scanType"]];
    [_py setMinMatchPercentage:[ud objectForKey:@"minMatchPercentage"]];
    [_py setWordWeighting:[ud objectForKey:@"wordWeighting"]];
    [_py setMixFileKind:n2b([ud objectForKey:@"mixFileKind"])];
    [_py setIgnoreHardlinkMatches:n2b([ud objectForKey:@"ignoreHardlinkMatches"])];
    [_py setMatchSimilarWords:[ud objectForKey:@"matchSimilarWords"]];
    int smallFileThreshold = [ud integerForKey:@"smallFileThreshold"]; // In KB
    int sizeThreshold = [ud boolForKey:@"ignoreSmallFiles"] ? smallFileThreshold * 1024 : 0; // The py side wants bytes
    [_py setSizeThreshold:sizeThreshold];
}

/* Actions */
- (IBAction)resetColumnsToDefault:(id)sender
{
    NSMutableArray *columnsOrder = [NSMutableArray array];
    [columnsOrder addObject:@"0"];
    [columnsOrder addObject:@"1"];
    [columnsOrder addObject:@"2"];
    [columnsOrder addObject:@"5"];
    NSMutableDictionary *columnsWidth = [NSMutableDictionary dictionary];
    [columnsWidth setObject:i2n(195) forKey:@"0"];
    [columnsWidth setObject:i2n(183) forKey:@"1"];
    [columnsWidth setObject:i2n(63) forKey:@"2"];
    [columnsWidth setObject:i2n(60) forKey:@"5"];
    [self restoreColumnsPosition:columnsOrder widths:columnsWidth];
}
@end
