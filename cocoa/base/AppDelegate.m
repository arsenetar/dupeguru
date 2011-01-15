/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "HSFairwareReminder.h"
#import "Utils.h"
#import "Consts.h"
#import "Dialogs.h"
#import <Sparkle/SUUpdater.h>

@implementation AppDelegateBase
- (void)awakeFromNib
{
    _recentResults = [[HSRecentFiles alloc] initWithName:@"recentResults" menu:recentResultsMenu];
    [_recentResults setDelegate:self];
    _resultWindow = [self createResultWindow];
    _directoryPanel = [self createDirectoryPanel];
    _detailsPanel = nil; // Lazily loaded
    _aboutBox = nil; // Lazily loaded
    _preferencesPanel = nil; // Lazily loaded
    [[[self directoryPanel] window] makeKeyAndOrderFront:self];
}

/* Virtual */

- (PyDupeGuruBase *)py { return py; }

- (ResultWindowBase *)createResultWindow
{
    return nil; // must be overriden by all editions
}

- (DirectoryPanel *)createDirectoryPanel
{
    return [[DirectoryPanel alloc] initWithParentApp:self];
}

- (DetailsPanel *)createDetailsPanel
{
    return [[DetailsPanel alloc] initWithPy:py];
}

- (NSString *)homepageURL
{
    return @""; // must be overriden by all editions
}

/* Public */
- (ResultWindowBase *)resultWindow
{
    return _resultWindow;
}

- (DirectoryPanel *)directoryPanel
{
    return _directoryPanel;
}

- (DetailsPanel *)detailsPanel
{
    if (!_detailsPanel)
        _detailsPanel = [self createDetailsPanel];
    return _detailsPanel;
}

- (HSRecentFiles *)recentResults
{
    return _recentResults;
}

- (NSMenu *)columnsMenu { return columnsMenu; }

/* Actions */
- (IBAction)loadResults:(id)sender
{
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:YES];
    [op setCanChooseDirectories:NO];
    [op setCanCreateDirectories:NO];
    [op setAllowsMultipleSelection:NO];
    [op setAllowedFileTypes:[NSArray arrayWithObject:@"dupeguru"]];
    [op setTitle:@"Select a results file to load"];
    if ([op runModal] == NSOKButton) {
        NSString *filename = [[op filenames] objectAtIndex:0];
        [py loadResultsFrom:filename];
        [[self recentResults] addFile:filename];
    }
}

- (IBAction)openWebsite:(id)sender
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:[self homepageURL]]];
}

- (IBAction)openHelp:(id)sender
{
    NSBundle *b = [NSBundle mainBundle];
    NSString *p = [b pathForResource:@"index" ofType:@"html" inDirectory:@"help"];
    NSURL *u = [NSURL fileURLWithPath:p];
    [[NSWorkspace sharedWorkspace] openURL:u];
}

- (IBAction)showAboutBox:(id)sender
{
    if (_aboutBox == nil) {
        _aboutBox = [[HSAboutBox alloc] initWithApp:py];
    }
    [[_aboutBox window] makeKeyAndOrderFront:sender];
}

- (IBAction)showDirectoryWindow:(id)sender
{
    [[[self directoryPanel] window] makeKeyAndOrderFront:nil];
}

- (IBAction)showPreferencesPanel:(id)sender
{
    if (_preferencesPanel == nil) {
        _preferencesPanel = [[NSWindowController alloc] initWithWindowNibName:@"Preferences"];
    }
    [_preferencesPanel showWindow:sender];
}

- (IBAction)showResultWindow:(id)sender
{
    [[[self resultWindow] window] makeKeyAndOrderFront:nil];
}

- (IBAction)startScanning:(id)sender
{
    [[self resultWindow] startDuplicateScan:sender];
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
        [[self resultWindow] restoreColumnsPosition:columnsOrder widths:columnsWidth];
    else
        [[self resultWindow] resetColumnsToDefault:nil];
    [HSFairwareReminder showNagWithApp:[self py]];
    [py loadSession];
}

- (void)applicationWillBecomeActive:(NSNotification *)aNotification
{
    if (![[[self directoryPanel] window] isVisible]) {
        [[self directoryPanel] showWindow:NSApp];
    }
}

- (NSApplicationTerminateReply)applicationShouldTerminate:(NSApplication *)sender
{
    if ([py resultsAreModified]) {
        NSString *msg = @"You have unsaved results, do you really want to quit?";
        if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) { // NO
            return NSTerminateCancel;
        }
    }
    return NSTerminateNow;
}

- (void)applicationWillTerminate:(NSNotification *)aNotification
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud setObject: [[self resultWindow] getColumnsOrder] forKey:@"columnsOrder"];
    [ud setObject: [[self resultWindow] getColumnsWidth] forKey:@"columnsWidth"];
    NSInteger sc = [ud integerForKey:@"sessionCountSinceLastIgnorePurge"];
    if (sc >= 10) {
        sc = -1;
        [py purgeIgnoreList];
    }
    sc++;
    [py saveSession];
    [ud setInteger:sc forKey:@"sessionCountSinceLastIgnorePurge"];
    // NSApplication does not release nib instances objects, we must do it manually
    // Well, it isn't needed because the memory is freed anyway (we are quitting the application
    // But I need to release HSRecentFiles so it saves the user defaults
    [_directoryPanel release];
    [_recentResults release];
}

- (void)recentFileClicked:(NSString *)path
{
    [py loadResultsFrom:path];
}
@end
