#import "AppDelegate.h"
#import "cocoalib/ProgressController.h"
#import "cocoalib/RegistrationInterface.h"
#import "cocoalib/Utils.h"
#import "cocoalib/ValueTransformers.h"
#import "Consts.h"

@implementation AppDelegate
+ (void)initialize
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSMutableDictionary *d = [NSMutableDictionary dictionary];
    [d setObject:i2n(1) forKey:@"scanType"];
    [d setObject:i2n(80) forKey:@"minMatchPercentage"];
    [d setObject:i2n(30) forKey:@"smallFileThreshold"];
    [d setObject:i2n(1) forKey:@"recreatePathType"];
    [d setObject:b2n(YES) forKey:@"wordWeighting"];
    [d setObject:b2n(NO) forKey:@"matchSimilarWords"];
    [d setObject:b2n(YES) forKey:@"mixFileKind"];
    [d setObject:b2n(NO) forKey:@"useRegexpFilter"];
    [d setObject:b2n(NO) forKey:@"removeEmptyFolders"];
    [d setObject:b2n(YES) forKey:@"ignoreSmallFiles"];
    [d setObject:b2n(NO) forKey:@"debug"];
    [d setObject:[NSArray array] forKey:@"recentDirectories"];
    [d setObject:[NSArray array] forKey:@"columnsOrder"];
    [d setObject:[NSDictionary dictionary] forKey:@"columnsWidth"];
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [ud registerDefaults:d];
}

- (id)init
{
    self = [super init];
    VTIsIntIn *vt = [[[VTIsIntIn alloc] initWithValues:[NSIndexSet indexSetWithIndex:1] reverse:YES] autorelease];
    [NSValueTransformer setValueTransformer:vt forName:@"vtScanTypeIsNotContent"];
    _directoryPanel = nil;
    _appName = APPNAME;
    return self;
}

- (IBAction)openWebsite:(id)sender
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://www.hardcoded.net/dupeguru"]];
}

- (IBAction)toggleDirectories:(id)sender
{
    [[self directoryPanel] toggleVisible:sender];
}

- (DirectoryPanel *)directoryPanel
{
    if (!_directoryPanel)
        _directoryPanel = [[DirectoryPanel alloc] initWithParentApp:self];
    return _directoryPanel;
}
- (PyDupeGuru *)py { return (PyDupeGuru *)py; }

//Delegate
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    [[ProgressController mainProgressController] setWorker:py];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    //Restore Columns
    NSArray *columnsOrder = [ud arrayForKey:@"columnsOrder"];
    NSDictionary *columnsWidth = [ud dictionaryForKey:@"columnsWidth"];
    if ([columnsOrder count])
        [result restoreColumnsPosition:columnsOrder widths:columnsWidth];
    //Reg stuff
    if ([RegistrationInterface showNagWithApp:[self py] name:APPNAME limitDescription:LIMIT_DESC])
        [unlockMenuItem setTitle:@"Thanks for buying dupeGuru!"];
    //Restore results
    [py loadIgnoreList];
    [py loadResults];
}

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
    [py saveResults];
    int sc = [ud integerForKey:@"sessionCountSinceLastIgnorePurge"];
    if (sc >= 10)
    {
        sc = -1;
        [py purgeIgnoreList];
    }
    sc++;
    [ud setInteger:sc forKey:@"sessionCountSinceLastIgnorePurge"];
    [py saveIgnoreList];
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
