/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "ResultWindow.h"
#import "ResultWindow_UI.h"
#import "Dialogs.h"
#import "ProgressController.h"
#import "Utils.h"
#import "AppDelegate.h"
#import "Consts.h"
#import "PrioritizeDialog.h"

@implementation ResultWindow

@synthesize optionsSwitch;
@synthesize optionsToolbarItem;
@synthesize matches;
@synthesize stats;
@synthesize filterField;

- (id)initWithParentApp:(AppDelegate *)aApp;
{
    self = [super initWithWindow:nil];
    app = aApp;
    model = [app model];
    [self setWindow:createResultWindow_UI(self)];
    [[self window] setTitle:fmt(NSLocalizedString(@"%@ Results", @""), [model appName])];
    /* Put a cute iTunes-like bottom bar */
    [[self window] setContentBorderThickness:28 forEdge:NSMinYEdge];
    table = [[ResultTable alloc] initWithPyRef:[model resultTable] view:matches];
    statsLabel = [[StatsLabel alloc] initWithPyRef:[model statsLabel] view:stats];
    [self initResultColumns:table];
    [[table columns] setColumnsAsReadOnly];
    [self fillColumnsMenu];
    [matches setTarget:self];
    [matches setDoubleAction:@selector(openClicked)];
    [self adjustUIToLocalization];
    return self;
}

- (void)dealloc
{
    [table release];
    [statsLabel release];
    [super dealloc];
}

/* Helpers */
- (void)fillColumnsMenu
{
    [[app columnsMenu] removeAllItems];
    NSArray *menuItems = [[[table columns] model] menuItems];
    for (NSInteger i=0; i < [menuItems count]; i++) {
        NSArray *pair = [menuItems objectAtIndex:i];
        NSString *display = [pair objectAtIndex:0];
        BOOL marked = n2b([pair objectAtIndex:1]);
        NSMenuItem *mi = [[app columnsMenu] addItemWithTitle:display action:@selector(toggleColumn:) keyEquivalent:@""];
        [mi setTarget:self];
        [mi setState:marked ? NSOnState : NSOffState];
        [mi setTag:i];
    }
    [[app columnsMenu] addItem:[NSMenuItem separatorItem]];
    NSMenuItem *mi = [[app columnsMenu] addItemWithTitle:NSLocalizedString(@"Reset to Default", @"")
        action:@selector(resetColumnsToDefault) keyEquivalent:@""];
    [mi setTarget:self];
}

- (void)updateOptionSegments
{
    [optionsSwitch setSelected:[[app detailsPanel] isVisible] forSegment:0];
    [optionsSwitch setSelected:[table powerMarkerMode] forSegment:1];
    [optionsSwitch setSelected:[table deltaValuesMode] forSegment:2];
}

- (void)adjustUIToLocalization
{
    NSString *lang = [[NSBundle preferredLocalizationsFromArray:[[NSBundle mainBundle] localizations]] objectAtIndex:0];
    NSInteger seg1delta = 0;
    NSInteger seg2delta = 0;
    if ([lang isEqual:@"ru"]) {
        seg2delta = 20;
    }
    else if ([lang isEqual:@"uk"]) {
        seg2delta = 20;
    }
    else if ([lang isEqual:@"hy"]) {
        seg1delta = 20;
    }
    if (seg1delta || seg2delta) {
        [optionsSwitch setWidth:[optionsSwitch widthForSegment:0]+seg1delta forSegment:0];
        [optionsSwitch setWidth:[optionsSwitch widthForSegment:1]+seg2delta forSegment:1];
        NSSize s = [optionsToolbarItem maxSize];
        s.width += seg1delta + seg2delta;
        [optionsToolbarItem setMaxSize:s];
        [optionsToolbarItem setMinSize:s];
    }
}

- (void)initResultColumns:(ResultTable *)aTable
{
    NSInteger appMode = [app getAppMode];
    if (appMode == AppModePicture) {
        HSColumnDef defs[] = {
            {@"marked", 26, 26, 26, YES, [NSButtonCell class]},
            {@"name", 162, 16, 0, YES, nil},
            {@"folder_path", 142, 16, 0, YES, nil},
            {@"size", 63, 16, 0, YES, nil},
            {@"extension", 40, 16, 0, YES, nil},
            {@"dimensions", 73, 16, 0, YES, nil},
            {@"exif_timestamp", 120, 16, 0, YES, nil},
            {@"mtime", 120, 16, 0, YES, nil},
            {@"percentage", 58, 16, 0, YES, nil},
            {@"dupe_count", 80, 16, 0, YES, nil},
            nil
        };
        [[aTable columns] initializeColumns:defs];
        NSTableColumn *c = [[aTable view] tableColumnWithIdentifier:@"marked"];
        [[c dataCell] setButtonType:NSSwitchButton];
        [[c dataCell] setControlSize:NSSmallControlSize];
        c = [[aTable view] tableColumnWithIdentifier:@"size"];
        [[c dataCell] setAlignment:NSRightTextAlignment];
    }
    else if (appMode == AppModeMusic) {
        HSColumnDef defs[] = {
            {@"marked", 26, 26, 26, YES, [NSButtonCell class]},
            {@"name", 235, 16, 0, YES, nil},
            {@"folder_path", 120, 16, 0, YES, nil},
            {@"size", 63, 16, 0, YES, nil},
            {@"duration", 50, 16, 0, YES, nil},
            {@"bitrate", 50, 16, 0, YES, nil},
            {@"samplerate", 60, 16, 0, YES, nil},
            {@"extension", 40, 16, 0, YES, nil},
            {@"mtime", 120, 16, 0, YES, nil},
            {@"title", 120, 16, 0, YES, nil},
            {@"artist", 120, 16, 0, YES, nil},
            {@"album", 120, 16, 0, YES, nil},
            {@"genre", 80, 16, 0, YES, nil},
            {@"year", 40, 16, 0, YES, nil},
            {@"track", 40, 16, 0, YES, nil},
            {@"comment", 120, 16, 0, YES, nil},
            {@"percentage", 57, 16, 0, YES, nil},
            {@"words", 120, 16, 0, YES, nil},
            {@"dupe_count", 80, 16, 0, YES, nil},
            nil
        };
        [[aTable columns] initializeColumns:defs];
        NSTableColumn *c = [[aTable view] tableColumnWithIdentifier:@"marked"];
        [[c dataCell] setButtonType:NSSwitchButton];
        [[c dataCell] setControlSize:NSSmallControlSize];
        c = [[aTable view] tableColumnWithIdentifier:@"size"];
        [[c dataCell] setAlignment:NSRightTextAlignment];
        c = [[aTable view] tableColumnWithIdentifier:@"duration"];
        [[c dataCell] setAlignment:NSRightTextAlignment];
        c = [[aTable view] tableColumnWithIdentifier:@"bitrate"];
        [[c dataCell] setAlignment:NSRightTextAlignment];
    }
    else {
        HSColumnDef defs[] = {
            {@"marked", 26, 26, 26, YES, [NSButtonCell class]},
            {@"name", 195, 16, 0, YES, nil},
            {@"folder_path", 183, 16, 0, YES, nil},
            {@"size", 63, 16, 0, YES, nil},
            {@"extension", 40, 16, 0, YES, nil},
            {@"mtime", 120, 16, 0, YES, nil},
            {@"percentage", 60, 16, 0, YES, nil},
            {@"words", 120, 16, 0, YES, nil},
            {@"dupe_count", 80, 16, 0, YES, nil},
            nil
        };
        [[aTable columns] initializeColumns:defs];
        NSTableColumn *c = [[aTable view] tableColumnWithIdentifier:@"marked"];
        [[c dataCell] setButtonType:NSSwitchButton];
        [[c dataCell] setControlSize:NSSmallControlSize];
        c = [[aTable view] tableColumnWithIdentifier:@"size"];
        [[c dataCell] setAlignment:NSRightTextAlignment];
    }
    [[aTable columns] restoreColumns];
}

/* Actions */
- (void)changeOptions
{
    NSInteger seg = [optionsSwitch selectedSegment];
    if (seg == 0) {
        [self toggleDetailsPanel];
    }
    else if (seg == 1) {
        [self togglePowerMarker];
    }
    else if (seg == 2) {
        [self toggleDelta];
    }
}

- (void)copyMarked
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [model setRemoveEmptyFolders:n2b([ud objectForKey:@"removeEmptyFolders"])];
    [model setCopyMoveDestType:n2i([ud objectForKey:@"recreatePathType"])];
    [model copyMarked];
}

- (void)trashMarked
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [model setRemoveEmptyFolders:n2b([ud objectForKey:@"removeEmptyFolders"])];
    [model deleteMarked];
}

- (void)filter
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [model setEscapeFilterRegexp:!n2b([ud objectForKey:@"useRegexpFilter"])];
    [model applyFilter:[filterField stringValue]];
}

- (void)focusOnFilterField
{
    [[self window] makeFirstResponder:filterField];
}

- (void)ignoreSelected
{
    [model addSelectedToIgnoreList];
}

- (void)invokeCustomCommand
{
    [model invokeCustomCommand];
}

- (void)markAll
{
    [model markAll];
}

- (void)markInvert
{
    [model markInvert];
}

- (void)markNone
{
    [model markNone];
}

- (void)markSelected
{
    [model toggleSelectedMark];
}

- (void)moveMarked
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [model setRemoveEmptyFolders:n2b([ud objectForKey:@"removeEmptyFolders"])];
    [model setCopyMoveDestType:n2i([ud objectForKey:@"recreatePathType"])];
    [model moveMarked];
}

- (void)openClicked
{
    if ([matches clickedRow] < 0) {
        return;
    }
    [matches selectRowIndexes:[NSIndexSet indexSetWithIndex:[matches clickedRow]] byExtendingSelection:NO];
    [model openSelected];
}

- (void)openSelected
{
    [model openSelected];
}

- (void)removeMarked
{
    [model removeMarked];
}

- (void)removeSelected
{
    [model removeSelected];
}

- (void)renameSelected
{
    NSInteger col = [matches columnWithIdentifier:@"name"];
    NSInteger row = [matches selectedRow];
    [matches editColumn:col row:row withEvent:[NSApp currentEvent] select:YES];
}

- (void)reprioritizeResults
{
    PrioritizeDialog *dlg = [[PrioritizeDialog alloc] initWithApp:model];
    NSInteger result = [NSApp runModalForWindow:[dlg window]];
    if (result == NSRunStoppedResponse) {
        [[dlg model] performReprioritization];
    }
    [dlg release];
    [[self window] makeKeyAndOrderFront:nil];
}

- (void)resetColumnsToDefault
{
    [[[table columns] model] resetToDefaults];
    [self fillColumnsMenu];
}

- (void)revealSelected
{
    [model revealSelected];
}

- (void)saveResults
{
    NSSavePanel *sp = [NSSavePanel savePanel];
    [sp setCanCreateDirectories:YES];
    [sp setAllowedFileTypes:[NSArray arrayWithObject:@"dupeguru"]];
    [sp setTitle:NSLocalizedString(@"Select a file to save your results to", @"")];
    if ([sp runModal] == NSOKButton) {
        [model saveResultsAs:[[sp URL] path]];
        [[app recentResults] addFile:[[sp URL] path]];
    }
}

- (void)switchSelected
{
    [model makeSelectedReference];
}

- (void)toggleColumn:(id)sender
{
    NSMenuItem *mi = sender;
    BOOL checked = [[[table columns] model] toggleMenuItem:[mi tag]];
    [mi setState:checked ? NSOnState : NSOffState];
}

- (void)toggleDetailsPanel
{
    [[app detailsPanel] toggleVisibility];
    [self updateOptionSegments];
}

- (void)toggleDelta
{
    [table setDeltaValuesMode:![table deltaValuesMode]];
    [self updateOptionSegments];
}

- (void)togglePowerMarker
{
    [table setPowerMarkerMode:![table powerMarkerMode]];
    [self updateOptionSegments];
}

- (void)toggleQuicklookPanel
{
    if ([QLPreviewPanel sharedPreviewPanelExists] && [[QLPreviewPanel sharedPreviewPanel] isVisible]) {
        [[QLPreviewPanel sharedPreviewPanel] orderOut:nil];
    } 
    else {
        [[QLPreviewPanel sharedPreviewPanel] makeKeyAndOrderFront:nil];
    }
}

/* Quicklook */
- (BOOL)acceptsPreviewPanelControl:(QLPreviewPanel *)panel;
{
    return YES;
}

- (void)beginPreviewPanelControl:(QLPreviewPanel *)panel
{
    // This document is now responsible of the preview panel
    // It is allowed to set the delegate, data source and refresh panel.
    previewPanel = [panel retain];
    panel.delegate = table;
    panel.dataSource = table;
}

- (void)endPreviewPanelControl:(QLPreviewPanel *)panel
{
    // This document loses its responsisibility on the preview panel
    // Until the next call to -beginPreviewPanelControl: it must not
    // change the panel's delegate, data source or refresh it.
    [previewPanel release];
    previewPanel = nil;
}

- (BOOL)validateToolbarItem:(NSToolbarItem *)theItem
{
    return ![[ProgressController mainProgressController] isShown];
}

- (BOOL)validateMenuItem:(NSMenuItem *)item
{
    if ([item action] == @selector(markAll)) {
        [item setTitle:NSLocalizedString(@"Mark All", @"")];
    }
    return ![[ProgressController mainProgressController] isShown];
}
@end
