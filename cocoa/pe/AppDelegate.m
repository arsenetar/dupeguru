/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "Utils.h"
#import "Dialogs.h"
#import "ValueTransformers.h"
#import "Consts.h"
#import "DetailsPanel.h"
#import "ResultWindow.h"

@implementation AppDelegate
+ (NSDictionary *)defaultPreferences
{
    NSMutableDictionary *d = [NSMutableDictionary dictionaryWithDictionary:[super defaultPreferences]];
    [d setObject:i2n(0) forKey:@"scanType"];
    [d setObject:i2n(95) forKey:@"minMatchPercentage"];
    [d setObject:b2n(NO) forKey:@"matchScaled"];
    return d;
}

- (id)init
{
    self = [super init];
    NSMutableIndexSet *i = [NSMutableIndexSet indexSetWithIndex:0];
    VTIsIntIn *vtScanTypeIsFuzzy = [[[VTIsIntIn alloc] initWithValues:i reverse:NO] autorelease];
    [NSValueTransformer setValueTransformer:vtScanTypeIsFuzzy forName:@"vtScanTypeIsFuzzy"];
    return self;
}

- (NSString *)homepageURL
{
    return @"https://www.hardcoded.net/dupeguru_pe/";
}

- (DetailsPanel *)createDetailsPanel
{
    return [[DetailsPanel alloc] initWithApp:model];
}

- (void)setScanOptions
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [model setScanType:n2i([ud objectForKey:@"scanType"])];
    [model setMinMatchPercentage:n2i([ud objectForKey:@"minMatchPercentage"])];
    [model setMixFileKind:n2b([ud objectForKey:@"mixFileKind"])];
    [model setIgnoreHardlinkMatches:n2b([ud objectForKey:@"ignoreHardlinkMatches"])];
    [model setMatchScaled:n2b([ud objectForKey:@"matchScaled"])];
}

- (void)initResultColumns:(ResultTable *)aTable
{
    HSColumnDef defs[] = {
        {@"marked", 26, 26, 26, YES, [NSButtonCell class]},
        {@"name", 162, 16, 0, YES, nil},
        {@"folder_path", 142, 16, 0, YES, nil},
        {@"size", 63, 16, 0, YES, nil},
        {@"extension", 40, 16, 0, YES, nil},
        {@"dimensions", 73, 16, 0, YES, nil},
        {@"exif_timestamp", 120, 16, 0, YES, nil},
        {@"mtime", 120, 16, 0, YES, nil},
        {@"percentage", 58, 16, 0, YES, nil},
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

- (void)clearPictureCache
{
    NSString *msg = NSLocalizedString(@"Do you really want to remove all your cached picture analysis?", @"");
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [model clearPictureCache];
}
@end
