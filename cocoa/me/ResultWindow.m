/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ResultWindow.h"
#import "Dialogs.h"
#import "Utils.h"
#import "PyDupeGuru.h"
#import "Consts.h"
#import "ProgressController.h"

@implementation ResultWindow
/* Override */
- (void)setScanOptions
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [model setScanType:n2i([ud objectForKey:@"scanType"])];
    [model enable:n2b([ud objectForKey:@"scanTagTrack"]) scanForTag:@"track"];
    [model enable:n2b([ud objectForKey:@"scanTagArtist"]) scanForTag:@"artist"];
    [model enable:n2b([ud objectForKey:@"scanTagAlbum"]) scanForTag:@"album"];
    [model enable:n2b([ud objectForKey:@"scanTagTitle"]) scanForTag:@"title"];
    [model enable:n2b([ud objectForKey:@"scanTagGenre"]) scanForTag:@"genre"];
    [model enable:n2b([ud objectForKey:@"scanTagYear"]) scanForTag:@"year"];
    [model setMinMatchPercentage:n2i([ud objectForKey:@"minMatchPercentage"])];
    [model setWordWeighting:n2b([ud objectForKey:@"wordWeighting"])];
    [model setMixFileKind:n2b([ud objectForKey:@"mixFileKind"])];
    [model setIgnoreHardlinkMatches:n2b([ud objectForKey:@"ignoreHardlinkMatches"])];
    [model setMatchSimilarWords:n2b([ud objectForKey:@"matchSimilarWords"])];
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
    [[table columns] initializeColumns:defs];
    NSTableColumn *c = [matches tableColumnWithIdentifier:@"marked"];
    [[c dataCell] setButtonType:NSSwitchButton];
    [[c dataCell] setControlSize:NSSmallControlSize];
    c = [matches tableColumnWithIdentifier:@"size"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [matches tableColumnWithIdentifier:@"duration"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [matches tableColumnWithIdentifier:@"bitrate"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[table columns] restoreColumns];
}

/* Actions */
- (IBAction)removeDeadTracks:(id)sender
{
    [model scanDeadTracks];
}
@end
