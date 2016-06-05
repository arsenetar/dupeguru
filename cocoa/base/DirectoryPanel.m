/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "DirectoryPanel.h"
#import "DirectoryPanel_UI.h"
#import "Dialogs.h"
#import "Utils.h"
#import "AppDelegate.h"

@implementation DirectoryPanel

@synthesize scanTypePopup;
@synthesize addButtonPopUp;
@synthesize loadRecentButtonPopUp;
@synthesize outlineView;
@synthesize removeButton;
@synthesize loadResultsButton;

- (id)initWithParentApp:(AppDelegateBase *)aParentApp
{
    self = [super initWithWindow:nil];
    [self setWindow:createDirectoryPanel_UI(self)];
    _app = aParentApp;
    model = [_app model];
    [[self window] setTitle:[model appName]];
    [[self scanTypePopup] addItemsWithTitles:[[aParentApp model] getScanOptions]];
    [[self scanTypePopup] bind:@"selectedIndex" toObject:[NSUserDefaultsController sharedUserDefaultsController] withKeyPath:@"values.scanType" options:nil];
    _alwaysShowPopUp = NO;
    [self fillPopUpMenu];
    _recentDirectories = [[HSRecentFiles alloc] initWithName:@"recentDirectories" menu:[addButtonPopUp menu]];
    [_recentDirectories setDelegate:self];
    outline = [[DirectoryOutline alloc] initWithPyRef:[model directoryTree] outlineView:outlineView];
    [self refreshRemoveButtonText];
    [self adjustUIToLocalization];
    
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(directorySelectionChanged:)
        name:NSOutlineViewSelectionDidChangeNotification object:outlineView];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(outlineAddedFolders:)
        name:DGAddedFoldersNotification object:outline];
    return self;
}

- (void)dealloc
{
    [outline release];
    [_recentDirectories release];
    [super dealloc];
}

/* Private */

- (void)fillPopUpMenu
{
    NSMenu *m = [addButtonPopUp menu];
    NSMenuItem *mi = [m addItemWithTitle:NSLocalizedString(@"Add New Folder...", @"") action:@selector(askForDirectory) keyEquivalent:@""];
    [mi setTarget:self];
    [m addItem:[NSMenuItem separatorItem]];
}

- (void)adjustUIToLocalization
{
    NSString *lang = [[NSBundle preferredLocalizationsFromArray:[[NSBundle mainBundle] localizations]] objectAtIndex:0];
    NSInteger loadResultsWidthDelta = 0;
    if ([lang isEqual:@"ru"]) {
        loadResultsWidthDelta = 50;
    }
    else if ([lang isEqual:@"uk"]) {
        loadResultsWidthDelta = 70;
    }
    else if ([lang isEqual:@"hy"]) {
        loadResultsWidthDelta = 30;
    }
    if (loadResultsWidthDelta) {
        NSRect r = [loadResultsButton frame];
        r.size.width += loadResultsWidthDelta;
        r.origin.x -= loadResultsWidthDelta;
        [loadResultsButton setFrame:r];
    }
}

/* Actions */

- (void)askForDirectory
{
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:YES];
    [op setCanChooseDirectories:YES];
    [op setAllowsMultipleSelection:YES];
    [op setTitle:NSLocalizedString(@"Select a folder to add to the scanning list", @"")];
    [op setDelegate:self];
    if ([op runModal] == NSOKButton) {
        for (NSURL *directoryURL in [op URLs]) {
            [self addDirectory:[directoryURL path]];
        }
    }
}

- (void)popupAddDirectoryMenu:(id)sender
{
    if ((!_alwaysShowPopUp) && ([[_recentDirectories filepaths] count] == 0)) {
        [self askForDirectory];
    }
    else {
        [addButtonPopUp selectItem:nil];
        [[addButtonPopUp cell] performClickWithFrame:[sender frame] inView:[sender superview]];
    }
}

- (void)popupLoadRecentMenu:(id)sender
{
    if ([[[_app recentResults] filepaths] count] > 0) {
        NSMenu *m = [loadRecentButtonPopUp menu];
        while ([m numberOfItems] > 0) {
            [m removeItemAtIndex:0];
        }
        NSMenuItem *mi = [m addItemWithTitle:NSLocalizedString(@"Load from file...", @"") action:@selector(loadResults) keyEquivalent:@""];
        [mi setTarget:_app];
        [m addItem:[NSMenuItem separatorItem]];
        [[_app recentResults] fillMenu:m];
        [loadRecentButtonPopUp selectItem:nil];
        [[loadRecentButtonPopUp cell] performClickWithFrame:[sender frame] inView:[sender superview]];
    }
    else {
        [_app loadResults];
    }
}

- (void)removeSelectedDirectory
{
    [[self window] makeKeyAndOrderFront:nil];
    [[outline model] removeSelectedDirectory];
    [self refreshRemoveButtonText];
}

- (void)startDuplicateScan
{
    if ([model resultsAreModified]) {
        if ([Dialogs askYesNo:NSLocalizedString(@"You have unsaved results, do you really want to continue?", @"")] == NSAlertSecondButtonReturn) // NO
            return;
    }
    [_app setScanOptions];
    [model doScan];
}

/* Public */
- (void)addDirectory:(NSString *)directory
{
    [model addDirectory:directory];
    [_recentDirectories addFile:directory];
    [[self window] makeKeyAndOrderFront:nil];
}

- (void)refreshRemoveButtonText
{
    if ([outlineView selectedRow] < 0) {
        [removeButton setEnabled:NO];
        return;
    }
    [removeButton setEnabled:YES];
    NSIndexPath *path = [outline selectedIndexPath];
    if (path != nil) {
        NSInteger state = [outline intProperty:@"state" valueAtPath:path];
        BOOL shouldDisplayArrow = ([path length] > 1) && (state == 2);
        NSString *imgName = shouldDisplayArrow ? @"NSGoLeftTemplate" : @"NSRemoveTemplate";
        [removeButton setImage:[NSImage imageNamed:imgName]];
    }
}

- (void)markAll
{
    /* markAll isn't very descriptive of what we do, but since we re-use the Mark All button from
       the result window, we don't have much choice.
    */
    [outline selectAll];
}

/* Delegate */
- (BOOL)panel:(id)sender shouldShowFilename:(NSString *)path
{
    BOOL isdir;
    [[NSFileManager defaultManager] fileExistsAtPath:path isDirectory:&isdir];
    return isdir;
}

- (void)recentFileClicked:(NSString *)path
{
    [self addDirectory:path];
}

- (BOOL)validateMenuItem:(NSMenuItem *)item
{
    if ([item action] == @selector(markAll)) {
        [item setTitle:NSLocalizedString(@"Select All", @"")];
    }
    return YES;
}

/* Notifications */

- (void)directorySelectionChanged:(NSNotification *)aNotification
{
    [self refreshRemoveButtonText];
}

- (void)outlineAddedFolders:(NSNotification *)aNotification
{
    NSArray *foldernames = [[aNotification userInfo] objectForKey:@"foldernames"];
    for (NSString *foldername in foldernames) {
        [_recentDirectories addFile:foldername];
    }
}

@end
