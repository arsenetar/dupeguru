/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "RegistrationInterface.h"
#import "Utils.h"
#import "Consts.h"
#import <Sparkle/SUUpdater.h>

@implementation AppDelegateBase
- (IBAction)unlockApp:(id)sender
{
    if ([[self py] isRegistered])
        return;
    RegistrationInterface *ri = [[RegistrationInterface alloc] initWithApp:[self py]];
    if ([ri enterCode] == NSOKButton)
    {
        NSString *menuTitle = [NSString stringWithFormat:@"Thanks for buying %@!",[py appName]];
        [unlockMenuItem setTitle:menuTitle];
    }
    [ri release];
}

- (PyDupeGuruBase *)py { return py; }
- (RecentDirectories *)recentDirectories { return recentDirectories; }
- (DirectoryPanel *)directoryPanel
{
    if (!_directoryPanel)
        _directoryPanel = [[DirectoryPanel alloc] initWithParentApp:self];
    return _directoryPanel;
}

- (DetailsPanel *)detailsPanel
{
    if (!_detailsPanel)
        _detailsPanel = [[DetailsPanel alloc] initWithPy:py];
    return _detailsPanel;
}

- (void)saveResults
{
    if (_savedResults) {
        return;
    }
    [py saveIgnoreList];
    [py saveResults];
    _savedResults = YES;
}

/* Delegate */
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    [[ProgressController mainProgressController] setWorker:py];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    //Restore Columns
    NSArray *columnsOrder = [ud arrayForKey:@"columnsOrder"];
    NSDictionary *columnsWidth = [ud dictionaryForKey:@"columnsWidth"];
    if ([columnsOrder count])
        [result restoreColumnsPosition:columnsOrder widths:columnsWidth];
    else
        [result resetColumnsToDefault:nil];
    //Reg stuff
    if ([RegistrationInterface showNagWithApp:[self py]])
        [unlockMenuItem setTitle:[NSString stringWithFormat:@"Thanks for buying %@!",[py appName]]];
    //Restore results
    [py loadIgnoreList];
    [py loadResults];
    _savedResults = NO;
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
    [self saveResults];
    NSInteger sc = [ud integerForKey:@"sessionCountSinceLastIgnorePurge"];
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

/* SUUpdater delegate */

- (BOOL)updater:(SUUpdater *)updater shouldPostponeRelaunchForUpdate:(SUAppcastItem *)update untilInvoking:(NSInvocation *)invocation;
{
    /* If results aren't saved now, we might get a weird utf-8 lookup error when saving later.
    **/
    [self saveResults];
    return NO;
}
@end
