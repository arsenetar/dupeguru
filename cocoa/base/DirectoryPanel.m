/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "DirectoryPanel.h"
#import "Dialogs.h"
#import "Utils.h"
#import "AppDelegate.h"

@implementation DirectoryPanel
- (id)initWithParentApp:(id)aParentApp
{
    self = [super initWithWindowNibName:@"DirectoryPanel"];
    [self window];
    AppDelegateBase *app = aParentApp;
    _py = [app py];
    _alwaysShowPopUp = NO;
    [self fillPopUpMenu];
    _recentDirectories = [[HSRecentFiles alloc] initWithName:@"recentDirectories" menu:[addButtonPopUp menu]];
    [_recentDirectories setDelegate:self];
    outline = [[DirectoryOutline alloc] initWithPyParent:_py view:outlineView];
    [self refreshRemoveButtonText];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(directorySelectionChanged:)
        name:NSOutlineViewSelectionDidChangeNotification object:outlineView];
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
    NSMenuItem *mi = [m addItemWithTitle:@"Add New Directory..." action:@selector(askForDirectory:) keyEquivalent:@""];
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
    [op setTitle:@"Select a directory to add to the scanning list"];
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

- (IBAction)removeSelectedDirectory:(id)sender
{
    [[self window] makeKeyAndOrderFront:nil];
    if ([outlineView selectedRow] < 0)
        return;
    NSIndexPath *path = [outline selectedIndexPath];
    NSInteger state = [outline intProperty:@"state" valueAtPath:path];
    if (([path length] == 1) && (state != 2)) {
        [_py removeDirectory:i2n([path indexAtPosition:0])];
    }
    else {
        NSInteger newState = state == 2 ? 0 : 2; // If excluded, put it back
        [outline setIntProperty:@"state" value:newState atPath:path];
        [outlineView display];
    }
    [self refreshRemoveButtonText];
}

- (IBAction)toggleVisible:(id)sender
{
    [[self window] makeKeyAndOrderFront:nil];
}

/* Public */
- (void)addDirectory:(NSString *)directory
{
    NSInteger r = [[_py addDirectory:directory] intValue];
    if (r) {
        NSString *m = @"";
        if (r == 1) {
            m = @"'%@' already is in the list.";
        }
        else if (r == 2) {
            m = @"'%@' does not exist.";
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
    NSInteger state = [outline intProperty:@"state" valueAtPath:[outline selectedIndexPath]];
    NSString *buttonText = state == 2 ? @"Put Back" : @"Remove";
    [removeButton setTitle:buttonText];
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

@end
