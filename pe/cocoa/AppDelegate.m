/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "RegistrationInterface.h"
#import "Utils.h"
#import "ValueTransformers.h"
#import "Consts.h"

@implementation AppDelegate
+ (void)initialize
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSMutableDictionary *d = [NSMutableDictionary dictionaryWithCapacity:10];
    [d setObject:[NSNumber numberWithInt:95] forKey:@"minMatchPercentage"];
    [d setObject:[NSNumber numberWithInt:1] forKey:@"recreatePathType"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"matchScaled"];
    [d setObject:[NSNumber numberWithBool:YES] forKey:@"mixFileKind"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"useRegexpFilter"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"removeEmptyFolders"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"debug"];
    [d setObject:[NSArray array] forKey:@"recentDirectories"];
    [d setObject:[NSArray array] forKey:@"columnsOrder"];
    [d setObject:[NSDictionary dictionary] forKey:@"columnsWidth"];
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [ud registerDefaults:d];
}

- (id)init
{
    self = [super init];
    _directoryPanel = nil;
    _detailsPanel = nil;
    _appName = APPNAME;
    return self;
}

- (IBAction)openWebsite:(id)sender
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://www.hardcoded.net/dupeguru_pe"]];
}

- (IBAction)toggleDetailsPanel:(id)sender
{
    if (!_detailsPanel)
        _detailsPanel = [[DetailsPanel alloc] initWithPy:py];
    if ([[_detailsPanel window] isVisible])
        [[_detailsPanel window] close];
    else
    {
        [[_detailsPanel window] orderFront:nil];
        [_detailsPanel refresh];
    }
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
        [unlockMenuItem setTitle:@"Thanks for buying dupeGuru Picture Edition!"];
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
