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
    HSColumnDef defs[] = {
        {@"marked", 26, 26, 26, NO, [NSButtonCell class]},
        {@"name", 235, 16, 0, YES, nil},
        {@"folder_path", 120, 16, 0, YES, nil},
        {@"size", 63, 16, 0, YES, nil},
        {@"duration", 50, 16, 0, YES, nil},
        {@"bitrate", 50, 16, 0, YES, nil},
        {@"samplerate", 60, 16, 0, YES, nil},
        {@"extension", 40, 16, 0, YES, nil},
        {@"mtime", 120, 16, 0, YES, nil},
        {@"title", 120, 16, 0, YES, nil},
        {@"artist", 120, 16, 0, YES, nil},
        {@"album", 120, 16, 0, YES, nil},
        {@"genre", 80, 16, 0, YES, nil},
        {@"year", 40, 16, 0, YES, nil},
        {@"track", 40, 16, 0, YES, nil},
        {@"comment", 120, 16, 0, YES, nil},
        {@"percentage", 57, 16, 0, YES, nil},
        {@"words", 120, 16, 0, YES, nil},
        {@"dupe_count", 80, 16, 0, YES, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [matches tableColumnWithIdentifier:@"marked"];
    [[c dataCell] setButtonType:NSSwitchButton];
    [[c dataCell] setControlSize:NSSmallControlSize];
    c = [[self tableView] tableColumnWithIdentifier:@"size"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self tableView] tableColumnWithIdentifier:@"duration"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self tableView] tableColumnWithIdentifier:@"bitrate"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[table columns] restoreColumns];
}

/* Actions */
- (IBAction)removeDeadTracks:(id)sender
{
    [(PyDupeGuru *)py scanDeadTracks];
}

/* Notifications */
- (void)jobCompleted:(NSNotification *)aNotification
{
    [super jobCompleted:aNotification];
    id lastAction = [[ProgressController mainProgressController] jobId];
    if ([lastAction isEqualTo:jobScanDeadTracks]) {
        NSInteger deadTrackCount = [(PyDupeGuru *)py deadTrackCount];
        if (deadTrackCount > 0) {
            NSString *msg = TR(@"Your iTunes Library contains %d dead tracks ready to be removed. Continue?");
            if ([Dialogs askYesNo:[NSString stringWithFormat:msg,deadTrackCount]] == NSAlertFirstButtonReturn)
                [(PyDupeGuru *)py removeDeadTracks];
        }
        else {
            [Dialogs showMessage:TR(@"You have no dead tracks in your iTunes Library")];
        }
    }
}
@end
