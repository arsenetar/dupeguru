/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "AppDelegate.h"
#import "../../cocoalib/ProgressController.h"
#import "../../cocoalib/Utils.h"
#import "../../cocoalib/ValueTransformers.h"
#import "../../cocoalib/Dialogs.h"
#import "DetailsPanel.h"
#import "DirectoryPanel.h"
#import "Consts.h"

@implementation AppDelegate
+ (void)initialize
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSMutableDictionary *d = [NSMutableDictionary dictionaryWithCapacity:10];
    [d setObject:i2n(3) forKey:@"scanType"];
    [d setObject:i2n(80) forKey:@"minMatchPercentage"];
    [d setObject:i2n(1) forKey:@"recreatePathType"];
    [d setObject:b2n(NO) forKey:@"wordWeighting"];
    [d setObject:b2n(NO) forKey:@"matchSimilarWords"];
    [d setObject:b2n(YES) forKey:@"mixFileKind"];
    [d setObject:b2n(NO) forKey:@"useRegexpFilter"];
    [d setObject:b2n(NO) forKey:@"ignoreHardlinkMatches"];
    [d setObject:b2n(NO) forKey:@"removeEmptyFolders"];
    [d setObject:b2n(NO) forKey:@"debug"];
    [d setObject:b2n(NO) forKey:@"scanTagTrack"];
    [d setObject:b2n(YES) forKey:@"scanTagArtist"];
    [d setObject:b2n(YES) forKey:@"scanTagAlbum"];
    [d setObject:b2n(YES) forKey:@"scanTagTitle"];
    [d setObject:b2n(NO) forKey:@"scanTagGenre"];
    [d setObject:b2n(NO) forKey:@"scanTagYear"];
    [d setObject:[NSArray array] forKey:@"recentDirectories"];
    [d setObject:[NSArray array] forKey:@"columnsOrder"];
    [d setObject:[NSDictionary dictionary] forKey:@"columnsWidth"];
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [ud registerDefaults:d];
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
    return @"http://www.hardcoded.net/dupeguru_me/"
}

- (DirectoryPanel *)directoryPanel
{
    if (!_directoryPanel)
        _directoryPanel = [[DirectoryPanelME alloc] initWithParentApp:self];
    return _directoryPanel;
}
- (PyDupeGuru *)py { return (PyDupeGuru *)py; }

//Delegate
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    NSMenu *actionsMenu = [[[NSApp mainMenu] itemWithTitle:@"Actions"] submenu];
    // index 3 is just after "Export Results to XHTML"
    NSMenuItem *mi = [actionsMenu insertItemWithTitle:@"Remove Dead Tracks in iTunes" 
        action:@selector(removeDeadTracks:) keyEquivalent:@"" atIndex:3];
    [mi setTarget:result];
    [super applicationDidFinishLaunching:aNotification];
}
@end
