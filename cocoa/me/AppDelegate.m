/* 
Copyright 2016 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "Utils.h"
#import "ValueTransformers.h"
#import "Dialogs.h"
#import "DetailsPanel.h"
#import "ResultWindow.h"
#import "Consts.h"

@implementation AppDelegate
+ (NSDictionary *)defaultPreferences
{
    NSMutableDictionary *d = [NSMutableDictionary dictionaryWithDictionary:[super defaultPreferences]];
    [d setObject:i2n(3) forKey:@"scanType"];
    [d setObject:i2n(80) forKey:@"minMatchPercentage"];
    [d setObject:b2n(NO) forKey:@"wordWeighting"];
    [d setObject:b2n(NO) forKey:@"matchSimilarWords"];
    [d setObject:b2n(NO) forKey:@"scanTagTrack"];
    [d setObject:b2n(YES) forKey:@"scanTagArtist"];
    [d setObject:b2n(YES) forKey:@"scanTagAlbum"];
    [d setObject:b2n(YES) forKey:@"scanTagTitle"];
    [d setObject:b2n(NO) forKey:@"scanTagGenre"];
    [d setObject:b2n(NO) forKey:@"scanTagYear"];
    return d;
}

- (id)init
{
    self = [super init];
    NSMutableIndexSet *i = [NSMutableIndexSet indexSetWithIndex:4];
    [i addIndex:5];
    VTIsIntIn *vtScanTypeIsNotContent = [[[VTIsIntIn alloc] initWithValues:i reverse:YES] autorelease];
    [NSValueTransformer setValueTransformer:vtScanTypeIsNotContent forName:@"vtScanTypeIsNotContent"];
    VTIsIntIn *vtScanTypeIsTag = [[[VTIsIntIn alloc] initWithValues:[NSIndexSet indexSetWithIndex:3] reverse:NO] autorelease];
    [NSValueTransformer setValueTransformer:vtScanTypeIsTag forName:@"vtScanTypeIsTag"];
    _directoryPanel = nil;
    return self;
}

- (NSString *)homepageURL
{
    return @"https://www.hardcoded.net/dupeguru_me/";
}

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

- (void)initResultColumns:(ResultTable *)aTable
{
    HSColumnDef defs[] = {
        {@"marked", 26, 26, 26, YES, [NSButtonCell class]},
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
    [[aTable columns] initializeColumns:defs];
    NSTableColumn *c = [[aTable view] tableColumnWithIdentifier:@"marked"];
    [[c dataCell] setButtonType:NSSwitchButton];
    [[c dataCell] setControlSize:NSSmallControlSize];
    c = [[aTable view] tableColumnWithIdentifier:@"size"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[aTable view] tableColumnWithIdentifier:@"duration"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[aTable view] tableColumnWithIdentifier:@"bitrate"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[aTable columns] restoreColumns];
}
@end
