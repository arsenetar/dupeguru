/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "HSFairwareReminder.h"
#import "HSPyUtil.h"
#import "Consts.h"
#import "Dialogs.h"
#import "ValueTransformers.h"
#import <Sparkle/SUUpdater.h>

@implementation AppDelegateBase
+ (void)initialize
{
    HSVTAdd *vt = [[[HSVTAdd alloc] initWithValue:4] autorelease];
    [NSValueTransformer setValueTransformer:vt forName:@"vtRowHeightOffset"];
}

- (void)awakeFromNib
{
    model = [[PyDupeGuru alloc] init];
    [model bindCallback:createCallback(@"DupeGuruView", self)];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    /* Because the pref pane is lazily loaded, we have to manually do the update check if the
       preference is set.
    */
    if ([ud boolForKey:@"SUEnableAutomaticChecks"]) {
        [[SUUpdater sharedUpdater] checkForUpdatesInBackground];
    }
    _recentResults = [[HSRecentFiles alloc] initWithName:@"recentResults" menu:recentResultsMenu];
    [_recentResults setDelegate:self];
    _resultWindow = [self createResultWindow];
    _directoryPanel = [self createDirectoryPanel];
    _detailsPanel = [self createDetailsPanel];
    _ignoreListDialog = [[IgnoreListDialog alloc] initWithPyRef:[model ignoreListDialog]];
    _aboutBox = nil; // Lazily loaded
    _preferencesPanel = nil; // Lazily loaded
    [[[self directoryPanel] window] makeKeyAndOrderFront:self];
}

/* Virtual */

- (PyDupeGuru *)model
{
    return model;
}

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
    return [[DetailsPanel alloc] initWithPyRef:[model detailsPanel]];
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
    [op setTitle:TR(@"Select a results file to load")];
    if ([op runModal] == NSOKButton) {
        NSString *filename = [[op filenames] objectAtIndex:0];
        [model loadResultsFrom:filename];
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
        _aboutBox = [[HSAboutBox alloc] initWithApp:model];
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

- (IBAction)showIgnoreList:(id)sender
{
    [model showIgnoreList];
}

- (IBAction)startScanning:(id)sender
{
    [[self resultWindow] startDuplicateScan:sender];
}


/* Delegate */
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    [[ProgressController mainProgressController] setWorker:model];
    [model initialRegistrationSetup];
    [model loadSession];
}

- (void)applicationWillBecomeActive:(NSNotification *)aNotification
{
    if (![[[self directoryPanel] window] isVisible]) {
        [[self directoryPanel] showWindow:NSApp];
    }
}

- (NSApplicationTerminateReply)applicationShouldTerminate:(NSApplication *)sender
{
    if ([model resultsAreModified]) {
        NSString *msg = TR(@"You have unsaved results, do you really want to quit?");
        if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) { // NO
            return NSTerminateCancel;
        }
    }
    return NSTerminateNow;
}

- (void)applicationWillTerminate:(NSNotification *)aNotification
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSInteger sc = [ud integerForKey:@"sessionCountSinceLastIgnorePurge"];
    if (sc >= 10) {
        sc = -1;
        [model purgeIgnoreList];
    }
    sc++;
    [model saveSession];
    [ud setInteger:sc forKey:@"sessionCountSinceLastIgnorePurge"];
    // NSApplication does not release nib instances objects, we must do it manually
    // Well, it isn't needed because the memory is freed anyway (we are quitting the application
    // But I need to release HSRecentFiles so it saves the user defaults
    [_directoryPanel release];
    [_recentResults release];
}

- (void)recentFileClicked:(NSString *)path
{
    [model loadResultsFrom:path];
}


/* model --> view */
- (void)showMessage:(NSString *)msg
{
    [Dialogs showMessage:msg];
}

- (BOOL)askYesNoWithPrompt:(NSString *)prompt
{
    return [Dialogs askYesNo:prompt] == NSAlertFirstButtonReturn;
}

- (void)showProblemDialog
{
    [[self resultWindow] showProblemDialog];
}

- (void)setupAsRegistered
{
    // Nothing to do.
}

- (void)showFairwareNagWithPrompt:(NSString *)prompt
{
    [HSFairwareReminder showFairwareNagWithApp:[self model] prompt:prompt];
}

- (void)showDemoNagWithPrompt:(NSString *)prompt
{
    [HSFairwareReminder showDemoNagWithApp:[self model] prompt:prompt];
}

- (NSString *)selectDestFolderWithPrompt:(NSString *)prompt
{
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:NO];
    [op setCanChooseDirectories:YES];
    [op setCanCreateDirectories:YES];
    [op setAllowsMultipleSelection:NO];
    [op setTitle:prompt];
    if ([op runModal] == NSOKButton) {
        return [[op filenames] objectAtIndex:0];
    }
    else {
        return nil;
    }
}

@end
