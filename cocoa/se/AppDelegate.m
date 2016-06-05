/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "Utils.h"
#import "ValueTransformers.h"
#import "DetailsPanel.h"
#import "DirectoryPanel.h"
#import "ResultWindow.h"
#import "Consts.h"

@implementation AppDelegate
+ (NSDictionary *)defaultPreferences
{
    NSMutableDictionary *d = [NSMutableDictionary dictionaryWithDictionary:[super defaultPreferences]];
    [d setObject:i2n(1) forKey:@"scanType"];
    [d setObject:i2n(80) forKey:@"minMatchPercentage"];
    [d setObject:i2n(30) forKey:@"smallFileThreshold"];
    [d setObject:b2n(YES) forKey:@"wordWeighting"];
    [d setObject:b2n(NO) forKey:@"matchSimilarWords"];
    [d setObject:b2n(YES) forKey:@"ignoreSmallFiles"];
    return d;
}

- (id)init
{
    self = [super init];
    NSMutableIndexSet *contentsIndexes = [NSMutableIndexSet indexSet];
    [contentsIndexes addIndex:1];
    [contentsIndexes addIndex:2];
    VTIsIntIn *vt = [[[VTIsIntIn alloc] initWithValues:contentsIndexes reverse:YES] autorelease];
    [NSValueTransformer setValueTransformer:vt forName:@"vtScanTypeIsNotContent"];
    _directoryPanel = nil;
    return self;
}

- (NSString *)homepageURL
{
    return @"http://www.hardcoded.net/dupeguru/";
}

- (void)setScanOptions
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [model setScanType:n2i([ud objectForKey:@"scanType"])];
    [model setMinMatchPercentage:n2i([ud objectForKey:@"minMatchPercentage"])];
    [model setWordWeighting:n2b([ud objectForKey:@"wordWeighting"])];
    [model setMixFileKind:n2b([ud objectForKey:@"mixFileKind"])];
    [model setIgnoreHardlinkMatches:n2b([ud objectForKey:@"ignoreHardlinkMatches"])];
    [model setMatchSimilarWords:n2b([ud objectForKey:@"matchSimilarWords"])];
    int smallFileThreshold = [ud integerForKey:@"smallFileThreshold"]; // In KB
    int sizeThreshold = [ud boolForKey:@"ignoreSmallFiles"] ? smallFileThreshold * 1024 : 0; // The py side wants bytes
    [model setSizeThreshold:sizeThreshold];
}

- (void)initResultColumns:(ResultTable *)aTable
{
    HSColumnDef defs[] = {
        {@"marked", 26, 26, 26, YES, [NSButtonCell class]},
        {@"name", 195, 16, 0, YES, nil},
        {@"folder_path", 183, 16, 0, YES, nil},
        {@"size", 63, 16, 0, YES, nil},
        {@"extension", 40, 16, 0, YES, nil},
        {@"mtime", 120, 16, 0, YES, nil},
        {@"percentage", 60, 16, 0, YES, nil},
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
    [[aTable columns] restoreColumns];
}

@end
