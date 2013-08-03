/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ResultWindowBase.h"
#import "ResultWindow_UI.h"
#import "Dialogs.h"
#import "ProgressController.h"
#import "Utils.h"
#import "AppDelegate.h"
#import "Consts.h"
#import "PrioritizeDialog.h"

@implementation ResultWindowBase

@synthesize optionsSwitch;
@synthesize optionsToolbarItem;
@synthesize matches;
@synthesize stats;
@synthesize filterField;

- (id)initWithParentApp:(AppDelegateBase *)aApp;
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
    problemDialog = [[ProblemDialog alloc] initWithPyRef:[model problemDialog]];
    deletionOptions = [[DeletionOptions alloc] initWithPyRef:[model deletionOptions]];
    [self initResultColumns];
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
    [problemDialog release];
    [super dealloc];
}

/* Virtual */
- (void)initResultColumns
{
}

- (void)setScanOptions
{
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

- (void)showProblemDialog
{
    [problemDialog showWindow:self];
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
        [model saveResultsAs:[sp filename]];
        [[app recentResults] addFile:[sp filename]];
    }
}

- (void)startDuplicateScan
{
    if ([model resultsAreModified]) {
        if ([Dialogs askYesNo:NSLocalizedString(@"You have unsaved results, do you really want to continue?", @"")] == NSAlertSecondButtonReturn) // NO
            return;
    }
    [self setScanOptions];
    [model doScan];
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
    return ![[ProgressController mainProgressController] isShown];
}
@end
