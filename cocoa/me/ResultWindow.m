/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ResultWindow.h"
#import "Dialogs.h"
#import "Utils.h"
#import "PyDupeGuru.h"
#import "Consts.h"

@implementation ResultWindow
/* Override */
- (void)setScanOptions
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    PyDupeGuru *_py = (PyDupeGuru *)py;
    [_py setScanType:[ud objectForKey:@"scanType"]];
    [_py enable:[ud objectForKey:@"scanTagTrack"] scanForTag:@"track"];
    [_py enable:[ud objectForKey:@"scanTagArtist"] scanForTag:@"artist"];
    [_py enable:[ud objectForKey:@"scanTagAlbum"] scanForTag:@"album"];
    [_py enable:[ud objectForKey:@"scanTagTitle"] scanForTag:@"title"];
    [_py enable:[ud objectForKey:@"scanTagGenre"] scanForTag:@"genre"];
    [_py enable:[ud objectForKey:@"scanTagYear"] scanForTag:@"year"];
    [_py setMinMatchPercentage:[ud objectForKey:@"minMatchPercentage"]];
    [_py setWordWeighting:[ud objectForKey:@"wordWeighting"]];
    [_py setMixFileKind:n2b([ud objectForKey:@"mixFileKind"])];
    [_py setIgnoreHardlinkMatches:n2b([ud objectForKey:@"ignoreHardlinkMatches"])];
    [_py setMatchSimilarWords:[ud objectForKey:@"matchSimilarWords"]];
}

- (void)initResultColumns
{
    NSTableColumn *refCol = [matches tableColumnWithIdentifier:@"0"];
    _resultColumns = [[NSMutableArray alloc] init];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"0"]]; // File Name
    [_resultColumns addObject:[self getColumnForIdentifier:1 title:TR(@"Folder") width:120 refCol:refCol]];
    NSTableColumn *sizeCol = [self getColumnForIdentifier:2 title:TR(@"Size (MB)") width:63 refCol:refCol];
    [[sizeCol dataCell] setAlignment:NSRightTextAlignment];
    [_resultColumns addObject:sizeCol];
    NSTableColumn *timeCol = [self getColumnForIdentifier:3 title:TR(@"Time") width:50 refCol:refCol];
    [[timeCol dataCell] setAlignment:NSRightTextAlignment];
    [_resultColumns addObject:timeCol];
    NSTableColumn *brCol = [self getColumnForIdentifier:4 title:TR(@"Bitrate") width:50 refCol:refCol];
    [[brCol dataCell] setAlignment:NSRightTextAlignment];
    [_resultColumns addObject:brCol];
    [_resultColumns addObject:[self getColumnForIdentifier:5 title:TR(@"Sample Rate") width:60 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:6 title:TR(@"Kind") width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:7 title:TR(@"Modification") width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:8 title:TR(@"Title") width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:9 title:TR(@"Artist") width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:10 title:TR(@"Album") width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:11 title:TR(@"Genre") width:80 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:12 title:TR(@"Year") width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:13 title:TR(@"Track Number") width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:14 title:TR(@"Comment") width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:15 title:TR(@"Match %") width:57 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:16 title:TR(@"Words Used") width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:17 title:TR(@"Dupe Count") width:80 refCol:refCol]];
}

/* Actions */
- (IBAction)removeDeadTracks:(id)sender
{
    [(PyDupeGuru *)py scanDeadTracks];
}

- (IBAction)resetColumnsToDefault:(id)sender
{
    NSMutableArray *columnsOrder = [NSMutableArray array];
    [columnsOrder addObject:@"0"];
    [columnsOrder addObject:@"2"];
    [columnsOrder addObject:@"3"];
    [columnsOrder addObject:@"4"];
    [columnsOrder addObject:@"6"];
    [columnsOrder addObject:@"15"];
    NSMutableDictionary *columnsWidth = [NSMutableDictionary dictionary];
    [columnsWidth setObject:i2n(235) forKey:@"0"];
    [columnsWidth setObject:i2n(63) forKey:@"2"];
    [columnsWidth setObject:i2n(50) forKey:@"3"];
    [columnsWidth setObject:i2n(50) forKey:@"4"];
    [columnsWidth setObject:i2n(40) forKey:@"6"];
    [columnsWidth setObject:i2n(57) forKey:@"15"];
    [self restoreColumnsPosition:columnsOrder widths:columnsWidth];
}

/* Notifications */
- (void)jobCompleted:(NSNotification *)aNotification
{
    [super jobCompleted:aNotification];
    id lastAction = [[ProgressController mainProgressController] jobId];
    if ([lastAction isEqualTo:jobScanDeadTracks]) {
        NSInteger deadTrackCount = [(PyDupeGuru *)py deadTrackCount];
        if (deadTrackCount > 0) {
            NSString *msg = TR(@"RemoveDeadTracksConfirmMsg");
            if ([Dialogs askYesNo:[NSString stringWithFormat:msg,deadTrackCount]] == NSAlertFirstButtonReturn)
                [(PyDupeGuru *)py removeDeadTracks];
        }
        else {
            [Dialogs showMessage:TR(@"NoDeadTrackMsg")];
        }
    }
}
@end
