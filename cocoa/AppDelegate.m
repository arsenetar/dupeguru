/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "HSPyUtil.h"
#import "Consts.h"
#import "Dialogs.h"
#import "Utils.h"
#import "ValueTransformers.h"
#import "DetailsPanelPicture.h"
#import "PreferencesPanelStandard_UI.h"
#import "PreferencesPanelMusic_UI.h"
#import "PreferencesPanelPicture_UI.h"

@implementation AppDelegate

@synthesize recentResultsMenu;
@synthesize columnsMenu;
@synthesize updater;

+ (NSDictionary *)defaultPreferences
{
    NSMutableDictionary *d = [NSMutableDictionary dictionary];
    [d setObject:i2n(1) forKey:@"scanTypeStandard"];
    [d setObject:i2n(3) forKey:@"scanTypeMusic"];
    [d setObject:i2n(0) forKey:@"scanTypePicture"];
    [d setObject:i2n(95) forKey:@"minMatchPercentage"];
    [d setObject:i2n(30) forKey:@"smallFileThreshold"];
    [d setObject:b2n(YES) forKey:@"wordWeighting"];
    [d setObject:b2n(NO) forKey:@"matchSimilarWords"];
    [d setObject:b2n(YES) forKey:@"ignoreSmallFiles"];
    [d setObject:b2n(NO) forKey:@"scanTagTrack"];
    [d setObject:b2n(YES) forKey:@"scanTagArtist"];
    [d setObject:b2n(YES) forKey:@"scanTagAlbum"];
    [d setObject:b2n(YES) forKey:@"scanTagTitle"];
    [d setObject:b2n(NO) forKey:@"scanTagGenre"];
    [d setObject:b2n(NO) forKey:@"scanTagYear"];
    [d setObject:b2n(NO) forKey:@"matchScaled"];
    [d setObject:i2n(1) forKey:@"recreatePathType"];
    [d setObject:i2n(11) forKey:TableFontSize];
    [d setObject:b2n(YES) forKey:@"mixFileKind"];
    [d setObject:b2n(NO) forKey:@"useRegexpFilter"];
    [d setObject:b2n(NO) forKey:@"ignoreHardlinkMatches"];
    [d setObject:b2n(NO) forKey:@"removeEmptyFolders"];
    [d setObject:b2n(NO) forKey:@"DebugMode"];
    [d setObject:@"" forKey:@"CustomCommand"];
    [d setObject:[NSArray array] forKey:@"recentDirectories"];
    [d setObject:[NSArray array] forKey:@"columnsOrder"];
    [d setObject:[NSDictionary dictionary] forKey:@"columnsWidth"];
    return d;
}

+ (void)initialize
{
    HSVTAdd *vt = [[[HSVTAdd alloc] initWithValue:4] autorelease];
    [NSValueTransformer setValueTransformer:vt forName:@"vtRowHeightOffset"];
    NSDictionary *d = [self defaultPreferences];
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [[NSUserDefaults standardUserDefaults] registerDefaults:d];
}

- (id)init
{
    self = [super init];
    model = [[PyDupeGuru alloc] init];
    [model bindCallback:createCallback(@"DupeGuruView", self)];
    [self setUpdater:[SUUpdater sharedUpdater]];
    NSMutableIndexSet *contentsIndexes = [NSMutableIndexSet indexSet];
    [contentsIndexes addIndex:1];
    [contentsIndexes addIndex:2];
    VTIsIntIn *vt = [[[VTIsIntIn alloc] initWithValues:contentsIndexes reverse:YES] autorelease];
    [NSValueTransformer setValueTransformer:vt forName:@"vtScanTypeIsNotContent"];
    NSMutableIndexSet *i = [NSMutableIndexSet indexSetWithIndex:0];
    VTIsIntIn *vtScanTypeIsFuzzy = [[[VTIsIntIn alloc] initWithValues:i reverse:NO] autorelease];
    [NSValueTransformer setValueTransformer:vtScanTypeIsFuzzy forName:@"vtScanTypeIsFuzzy"];
    i = [NSMutableIndexSet indexSetWithIndex:4];
    [i addIndex:5];
    VTIsIntIn *vtScanTypeIsNotContent = [[[VTIsIntIn alloc] initWithValues:i reverse:YES] autorelease];
    [NSValueTransformer setValueTransformer:vtScanTypeIsNotContent forName:@"vtScanTypeMusicIsNotContent"];
    VTIsIntIn *vtScanTypeIsTag = [[[VTIsIntIn alloc] initWithValues:[NSIndexSet indexSetWithIndex:3] reverse:NO] autorelease];
    [NSValueTransformer setValueTransformer:vtScanTypeIsTag forName:@"vtScanTypeIsTag"];
    return self;
}

- (void)finalizeInit
{
    // We can only finalize initialization once the main menu has been created, which cannot happen
    // before AppDelegate is created.
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    /* Because the pref pane is lazily loaded, we have to manually do the update check if the
       preference is set.
    */
    if ([ud boolForKey:@"SUEnableAutomaticChecks"]) {
        [[SUUpdater sharedUpdater] checkForUpdatesInBackground];
    }
    _recentResults = [[HSRecentFiles alloc] initWithName:@"recentResults" menu:recentResultsMenu];
    [_recentResults setDelegate:self];
    _directoryPanel = [[DirectoryPanel alloc] initWithParentApp:self];
    _ignoreListDialog = [[IgnoreListDialog alloc] initWithPyRef:[model ignoreListDialog]];
    _problemDialog = [[ProblemDialog alloc] initWithPyRef:[model problemDialog]];
    _deletionOptions = [[DeletionOptions alloc] initWithPyRef:[model deletionOptions]];
    _progressWindow = [[HSProgressWindow alloc] initWithPyRef:[[self model] progressWindow] view:nil];
    [_progressWindow setParentWindow:[_directoryPanel window]];
     // Lazily loaded
    _aboutBox = nil;
    _preferencesPanel = nil;
    _resultWindow = nil;
    _detailsPanel = nil;
    [[[self directoryPanel] window] makeKeyAndOrderFront:self];
}

/* Virtual */

- (PyDupeGuru *)model
{
    return model;
}

- (DetailsPanel *)createDetailsPanel
{
    NSInteger appMode = [self getAppMode];
    if (appMode == AppModePicture) {
        return [[DetailsPanelPicture alloc] initWithPyRef:[model detailsPanel]];
    }
    else {
        return [[DetailsPanel alloc] initWithPyRef:[model detailsPanel]];
    }
}

- (void)setScanOptions
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSString *scanTypeOptionName;
    NSInteger appMode = [self getAppMode];
    if (appMode == AppModePicture) {
        scanTypeOptionName = @"scanTypePicture";
    }
    else if (appMode == AppModeMusic) {
        scanTypeOptionName = @"scanTypeMusic";
    }
    else {
        scanTypeOptionName = @"scanTypeStandard";
    }
    [model setScanType:n2i([ud objectForKey:scanTypeOptionName])];
    [model setMinMatchPercentage:n2i([ud objectForKey:@"minMatchPercentage"])];
    [model setWordWeighting:n2b([ud objectForKey:@"wordWeighting"])];
    [model setMixFileKind:n2b([ud objectForKey:@"mixFileKind"])];
    [model setIgnoreHardlinkMatches:n2b([ud objectForKey:@"ignoreHardlinkMatches"])];
    [model setMatchSimilarWords:n2b([ud objectForKey:@"matchSimilarWords"])];
    int smallFileThreshold = [ud integerForKey:@"smallFileThreshold"]; // In KB
    int sizeThreshold = [ud boolForKey:@"ignoreSmallFiles"] ? smallFileThreshold * 1024 : 0; // The py side wants bytes
    [model setSizeThreshold:sizeThreshold];
    [model enable:n2b([ud objectForKey:@"scanTagTrack"]) scanForTag:@"track"];
    [model enable:n2b([ud objectForKey:@"scanTagArtist"]) scanForTag:@"artist"];
    [model enable:n2b([ud objectForKey:@"scanTagAlbum"]) scanForTag:@"album"];
    [model enable:n2b([ud objectForKey:@"scanTagTitle"]) scanForTag:@"title"];
    [model enable:n2b([ud objectForKey:@"scanTagGenre"]) scanForTag:@"genre"];
    [model enable:n2b([ud objectForKey:@"scanTagYear"]) scanForTag:@"year"];
    [model setMatchScaled:n2b([ud objectForKey:@"matchScaled"])];
}

/* Public */
- (ResultWindow *)resultWindow
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

- (NSInteger)getAppMode
{
    return [model getAppMode];
}

- (void)setAppMode:(NSInteger)appMode
{
    [model setAppMode:appMode];
    if (_preferencesPanel != nil) {
        [_preferencesPanel release];
        _preferencesPanel = nil;
    }
}

/* Actions */
- (void)clearPictureCache
{
    NSString *msg = NSLocalizedString(@"Do you really want to remove all your cached picture analysis?", @"");
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [model clearPictureCache];
}

- (void)loadResults
{
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:YES];
    [op setCanChooseDirectories:NO];
    [op setCanCreateDirectories:NO];
    [op setAllowsMultipleSelection:NO];
    [op setAllowedFileTypes:[NSArray arrayWithObject:@"dupeguru"]];
    [op setTitle:NSLocalizedString(@"Select a results file to load", @"")];
    if ([op runModal] == NSOKButton) {
        NSString *filename = [[[op URLs] objectAtIndex:0] path];
        [model loadResultsFrom:filename];
        [[self recentResults] addFile:filename];
    }
}

- (void)openWebsite
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://www.hardcoded.net/dupeguru/"]];
}

- (void)openHelp
{
    NSBundle *b = [NSBundle mainBundle];
    NSString *p = [b pathForResource:@"index" ofType:@"html" inDirectory:@"help"];
    NSURL *u = [NSURL fileURLWithPath:p];
    [[NSWorkspace sharedWorkspace] openURL:u];
}

- (void)showAboutBox
{
    if (_aboutBox == nil) {
        _aboutBox = [[HSAboutBox alloc] initWithApp:model];
    }
    [[_aboutBox window] makeKeyAndOrderFront:nil];
}

- (void)showDirectoryWindow
{
    [[[self directoryPanel] window] makeKeyAndOrderFront:nil];
}

- (void)showPreferencesPanel
{
    if (_preferencesPanel == nil) {
        NSWindow *window;
        NSInteger appMode = [model getAppMode];
        if (appMode == AppModePicture) {
            window = createPreferencesPanelPicture_UI(nil);
        }
        else if (appMode == AppModeMusic) {
            window = createPreferencesPanelMusic_UI(nil);
        }
        else {
            window = createPreferencesPanelStandard_UI(nil);
        }
        _preferencesPanel = [[NSWindowController alloc] initWithWindow:window];
    }
    [_preferencesPanel showWindow:nil];
}

- (void)showResultWindow
{
    [[[self resultWindow] window] makeKeyAndOrderFront:nil];
}

- (void)showIgnoreList
{
    [model showIgnoreList];
}

- (void)startScanning
{
    [[self directoryPanel] startDuplicateScan];
}


/* Delegate */
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
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
        NSString *msg = NSLocalizedString(@"You have unsaved results, do you really want to quit?", @"");
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

- (void)createResultsWindow
{
    if (_resultWindow != nil) {
        [_resultWindow release];
    }
    if (_detailsPanel != nil) {
        [_detailsPanel release];
    }
    _resultWindow = [[ResultWindow alloc] initWithParentApp:self];
    _detailsPanel = [self createDetailsPanel];
}
- (void)showResultsWindow
{
    [[[self resultWindow] window] makeKeyAndOrderFront:nil];
}

- (void)showProblemDialog
{
    [_problemDialog showWindow:self];
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
        return [[[op URLs] objectAtIndex:0] path];
    }
    else {
        return nil;
    }
}

- (NSString *)selectDestFileWithPrompt:(NSString *)prompt extension:(NSString *)extension
{
    NSSavePanel *sp = [NSSavePanel savePanel];
    [sp setCanCreateDirectories:YES];
    [sp setAllowedFileTypes:[NSArray arrayWithObject:extension]];
    [sp setTitle:prompt];
    if ([sp runModal] == NSOKButton) {
        return [[sp URL] path];
    }
    else {
        return nil;
    }
}

@end
