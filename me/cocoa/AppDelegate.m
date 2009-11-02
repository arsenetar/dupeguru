/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "AppDelegate.h"
#import "cocoalib/ProgressController.h"
#import "cocoalib/RegistrationInterface.h"
#import "cocoalib/Utils.h"
#import "cocoalib/ValueTransformers.h"
#import "cocoalib/Dialogs.h"
#import "DetailsPanel.h"
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
    _appName = APPNAME;
    return self;
}

- (IBAction)openWebsite:(id)sender
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://www.hardcoded.net/dupeguru_me"]];
}

- (IBAction)toggleDirectories:(id)sender
{
    [[self directoryPanel] toggleVisible:sender];
}


- (DetailsPanelBase *)detailsPanel
{
    if (!_detailsPanel)
        _detailsPanel = [[DetailsPanel alloc] initWithPy:py];
    return _detailsPanel;
}

- (DirectoryPanel *)directoryPanel
{
    if (!_directoryPanel)
        _directoryPanel = [[DirectoryPanel alloc] initWithParentApp:self];
    return _directoryPanel;
}
- (PyDupeGuru *)py { return (PyDupeGuru *)py; }

//Delegate
- (void)applicationWillBecomeActive:(NSNotification *)aNotification
{
    if (![[result window] isVisible])
        [result showWindow:NSApp];
}

- (void)applicationWillTerminate:(NSNotification *)aNotification
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud setObject: [result getColumnsOrder] forKey:@"columnsOrder"];
    [ud setObject: [result getColumnsWidth] forKey:@"columnsWidth"];
    [py saveIgnoreList];
    [py saveResults];
    int sc = [ud integerForKey:@"sessionCountSinceLastIgnorePurge"];
    if (sc >= 10)
    {
        sc = -1;
        [py purgeIgnoreList];
    }
    sc++;
    [ud setInteger:sc forKey:@"sessionCountSinceLastIgnorePurge"];
    // NSApplication does not release nib instances objects, we must do it manually
    // Well, it isn't needed because the memory is freed anyway (we are quitting the application
    // But I need to release RecentDirectories so it saves the user defaults
    [recentDirectories release];
}

- (void)recentDirecoryClicked:(NSString *)directory
{
    [[self directoryPanel] addDirectory:directory];
}
@end
