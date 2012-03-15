/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "DirectoryPanel.h"
#import "Dialogs.h"
#import "Utils.h"
#import "AppDelegate.h"
#import "Consts.h"

@implementation DirectoryPanel
- (id)initWithParentApp:(AppDelegateBase *)aParentApp
{
    self = [super initWithWindowNibName:@"DirectoryPanel"];
    [self window];
    _app = aParentApp;
    model = [_app model];
    [[self window] setTitle:[model appName]];
    _alwaysShowPopUp = NO;
    [self fillPopUpMenu];
    _recentDirectories = [[HSRecentFiles alloc] initWithName:@"recentDirectories" menu:[addButtonPopUp menu]];
    [_recentDirectories setDelegate:self];
    outline = [[DirectoryOutline alloc] initWithPyRef:[model directoryTree] outlineView:outlineView];
    [self refreshRemoveButtonText];
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

/* Virtual */

- (void)fillPopUpMenu
{
    NSMenu *m = [addButtonPopUp menu];
    NSMenuItem *mi = [m addItemWithTitle:TR(@"Add New Folder...") action:@selector(askForDirectory:) keyEquivalent:@""];
    [mi setTarget:self];
    [m addItem:[NSMenuItem separatorItem]];
}

/* Actions */

- (IBAction)askForDirectory:(id)sender
{
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:YES];
    [op setCanChooseDirectories:YES];
    [op setAllowsMultipleSelection:YES];
    [op setTitle:TR(@"Select a folder to add to the scanning list")];
    [op setDelegate:self];
    if ([op runModal] == NSOKButton) {
        for (NSString *directory in [op filenames]) {
            [self addDirectory:directory];
        }
    }
}

- (IBAction)popupAddDirectoryMenu:(id)sender
{
    if ((!_alwaysShowPopUp) && ([[_recentDirectories filepaths] count] == 0)) {
        [self askForDirectory:sender];
    }
    else {
        [addButtonPopUp selectItem:nil];
        [[addButtonPopUp cell] performClickWithFrame:[sender frame] inView:[sender superview]];
    }
}

- (IBAction)popupLoadRecentMenu:(id)sender
{
    if ([[[_app recentResults] filepaths] count] > 0) {
        NSMenu *m = [loadRecentButtonPopUp menu];
        while ([m numberOfItems] > 0) {
            [m removeItemAtIndex:0];
        }
        NSMenuItem *mi = [m addItemWithTitle:TR(@"Load from file...") action:@selector(loadResults:) keyEquivalent:@""];
        [mi setTarget:_app];
        [m addItem:[NSMenuItem separatorItem]];
        [[_app recentResults] fillMenu:m];
        [loadRecentButtonPopUp selectItem:nil];
        [[loadRecentButtonPopUp cell] performClickWithFrame:[sender frame] inView:[sender superview]];
    }
    else {
        [_app loadResults:nil];
    }
}

- (IBAction)removeSelectedDirectory:(id)sender
{
    [[self window] makeKeyAndOrderFront:nil];
    [[outline model] removeSelectedDirectory];
    [self refreshRemoveButtonText];
}

/* Public */
- (void)addDirectory:(NSString *)directory
{
    NSInteger r = [model addDirectory:directory];
    if (r) {
        NSString *m = @"";
        if (r == 1) {
            m = TR(@"'%@' already is in the list.");
        }
        else if (r == 2) {
            m = TR(@"'%@' does not exist.");
        }
        [Dialogs showMessage:[NSString stringWithFormat:m,directory]];
    }
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
