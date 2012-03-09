/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ResultWindow.h"
#import "Dialogs.h"
#import "ProgressController.h"
#import "Utils.h"
#import "AppDelegate.h"
#import "Consts.h"
#import "PrioritizeDialog.h"

@implementation ResultWindowBase
- (id)initWithParentApp:(AppDelegateBase *)aApp;
{
    self = [super initWithWindowNibName:@"ResultWindow"];
    app = aApp;
    model = [app model];
    [[self window] setTitle:fmt(@"%@ Results", [model appName])];
    columnsMenu = [app columnsMenu];
    /* Put a cute iTunes-like bottom bar */
    [[self window] setContentBorderThickness:28 forEdge:NSMinYEdge];
    table = [[ResultTable alloc] initWithPyRef:[model resultTable] view:matches];
    statsLabel = [[StatsLabel alloc] initWithPyRef:[model statsLabel] view:stats];
    problemDialog = [[ProblemDialog alloc] initWithPyRef:[model problemDialog]];
    [self initResultColumns];
    [self fillColumnsMenu];
    [matches setTarget:self];
    [matches setDoubleAction:@selector(openClicked:)];
    
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobStarted:) name:JobStarted object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobInProgress:) name:JobInProgress object:nil];
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
    NSArray *menuItems = [[[table columns] model] menuItems];
    for (NSInteger i=0; i < [menuItems count]; i++) {
        NSArray *pair = [menuItems objectAtIndex:i];
        NSString *display = [pair objectAtIndex:0];
        BOOL marked = n2b([pair objectAtIndex:1]);
        NSMenuItem *mi = [columnsMenu addItemWithTitle:display action:@selector(toggleColumn:) keyEquivalent:@""];
        [mi setTarget:self];
        [mi setState:marked ? NSOnState : NSOffState];
        [mi setTag:i];
    }
    [columnsMenu addItem:[NSMenuItem separatorItem]];
    NSMenuItem *mi = [columnsMenu addItemWithTitle:TR(@"Reset to Default")
        action:@selector(resetColumnsToDefault:) keyEquivalent:@""];
    [mi setTarget:self];
}

- (void)sendMarkedToTrash:(BOOL)hardlinkDeleted
{
    NSInteger mark_count = [model getMarkCount];
    if (!mark_count) {
        return;
    }
    NSString *msg = TR(@"You are about to send %d files to Trash. Continue?");
    if (hardlinkDeleted) {
        msg = TR(@"You are about to send %d files to Trash (and hardlink them afterwards). Continue?");
    }
    if ([Dialogs askYesNo:[NSString stringWithFormat:msg,mark_count]] == NSAlertSecondButtonReturn) { // NO
        return;
    }
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [model setRemoveEmptyFolders:n2b([ud objectForKey:@"removeEmptyFolders"])];
    if (hardlinkDeleted) {
        [model hardlinkMarked];
    }
    else {
        [model deleteMarked];
    }
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

/* Actions */
- (IBAction)clearIgnoreList:(id)sender
{
    NSInteger i = [model getIgnoreListCount];
    if (!i)
        return;
    NSString *msg = [NSString stringWithFormat:TR(@"Do you really want to remove all %d items from the ignore list?"),i];
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [model clearIgnoreList];
}

- (IBAction)changeOptions:(id)sender
{
    NSInteger seg = [optionsSwitch selectedSegment];
    if (seg == 0) {
        [self toggleDetailsPanel:sender];
    }
    else if (seg == 1) {
        [self togglePowerMarker:sender];
    }
    else if (seg == 2) {
        [self toggleDelta:sender];
    }
}

- (IBAction)copyMarked:(id)sender
{
    NSInteger mark_count = [model getMarkCount];
    if (!mark_count)
        return;
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:NO];
    [op setCanChooseDirectories:YES];
    [op setCanCreateDirectories:YES];
    [op setAllowsMultipleSelection:NO];
    [op setTitle:TR(@"Select a directory to copy marked files to")];
    if ([op runModal] == NSOKButton) {
        NSString *directory = [[op filenames] objectAtIndex:0];
        NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
        [model copyOrMove:YES markedTo:directory recreatePath:n2b([ud objectForKey:@"recreatePathType"])];
    }
}

- (IBAction)deleteMarked:(id)sender
{
    [self sendMarkedToTrash:NO];
}

- (IBAction)hardlinkMarked:(id)sender
{
    [self sendMarkedToTrash:YES];
}

- (IBAction)exportToXHTML:(id)sender
{
    NSString *exported = [model exportToXHTML];
    [[NSWorkspace sharedWorkspace] openFile:exported];
}

- (IBAction)filter:(id)sender
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [model setEscapeFilterRegexp:!n2b([ud objectForKey:@"useRegexpFilter"])];
    [model applyFilter:[filterField stringValue]];
}

- (IBAction)ignoreSelected:(id)sender
{
    NSInteger selectedDupeCount = [table selectedDupeCount];
    if (!selectedDupeCount)
        return;
    NSString *msg = [NSString stringWithFormat:TR(@"All selected %d matches are going to be ignored in all subsequent scans. Continue?"),selectedDupeCount];
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [model addSelectedToIgnoreList];
}

- (IBAction)invokeCustomCommand:(id)sender
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSString *cmd = [ud stringForKey:@"CustomCommand"];
    if ((cmd != nil) && ([cmd length] > 0)) {
        [model invokeCommand:cmd];
    }
    else {
        [Dialogs showMessage:TR(@"You have no custom command set up. Set it up in your preferences.")];
    }
}

- (IBAction)markAll:(id)sender
{
    [model markAll];
}

- (IBAction)markInvert:(id)sender
{
    [model markInvert];
}

- (IBAction)markNone:(id)sender
{
    [model markNone];
}

- (IBAction)markSelected:(id)sender
{
    [model toggleSelectedMark];
}

- (IBAction)moveMarked:(id)sender
{
    NSInteger mark_count = [model getMarkCount];
    if (!mark_count)
        return;
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:NO];
    [op setCanChooseDirectories:YES];
    [op setCanCreateDirectories:YES];
    [op setAllowsMultipleSelection:NO];
    [op setTitle:TR(@"Select a directory to move marked files to")];
    if ([op runModal] == NSOKButton) {
        NSString *directory = [[op filenames] objectAtIndex:0];
        NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
        [model setRemoveEmptyFolders:n2b([ud objectForKey:@"removeEmptyFolders"])];
        [model copyOrMove:NO markedTo:directory recreatePath:n2b([ud objectForKey:@"recreatePathType"])];
    }
}

- (IBAction)openClicked:(id)sender
{
    if ([matches clickedRow] < 0) {
        return;
    }
    [matches selectRowIndexes:[NSIndexSet indexSetWithIndex:[matches clickedRow]] byExtendingSelection:NO];
    [model openSelected];
}

- (IBAction)openSelected:(id)sender
{
    [model openSelected];
}

- (IBAction)removeMarked:(id)sender
{
    int mark_count = [model getMarkCount];
    if (!mark_count)
        return;
    NSString *msg = [NSString stringWithFormat:@"You are about to remove %d files from results. Continue?",mark_count];
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [model removeMarked];
}

- (IBAction)removeSelected:(id)sender
{
    [table removeSelected];
}

- (IBAction)renameSelected:(id)sender
{
    NSInteger col = [matches columnWithIdentifier:@"0"];
    NSInteger row = [matches selectedRow];
    [matches editColumn:col row:row withEvent:[NSApp currentEvent] select:YES];
}

- (IBAction)reprioritizeResults:(id)sender
{
    PrioritizeDialog *dlg = [[PrioritizeDialog alloc] initWithApp:model];
    NSInteger result = [NSApp runModalForWindow:[dlg window]];
    if (result == NSRunStoppedResponse) {
        [[dlg model] performReprioritization];
    }
    [dlg release];
    [[self window] makeKeyAndOrderFront:nil];
}

- (IBAction)resetColumnsToDefault:(id)sender
{
    [[[table columns] model] resetToDefaults];
}

- (IBAction)revealSelected:(id)sender
{
    [model revealSelected];
}

- (IBAction)saveResults:(id)sender
{
    NSSavePanel *sp = [NSSavePanel savePanel];
    [sp setCanCreateDirectories:YES];
    [sp setAllowedFileTypes:[NSArray arrayWithObject:@"dupeguru"]];
    [sp setTitle:TR(@"Select a file to save your results to")];
    if ([sp runModal] == NSOKButton) {
        [model saveResultsAs:[sp filename]];
        [[app recentResults] addFile:[sp filename]];
    }
}

- (IBAction)startDuplicateScan:(id)sender
{
    if ([model resultsAreModified]) {
        if ([Dialogs askYesNo:TR(@"You have unsaved results, do you really want to continue?")] == NSAlertSecondButtonReturn) // NO
            return;
    }
    [self setScanOptions];
    [model doScan];
}

- (IBAction)switchSelected:(id)sender
{
    [model makeSelectedReference];
}

- (IBAction)toggleColumn:(id)sender
{
    NSMenuItem *mi = sender;
    BOOL checked = [[[table columns] model] toggleMenuItem:[mi tag]];
    [mi setState:checked ? NSOnState : NSOffState];
}

- (IBAction)toggleDetailsPanel:(id)sender
{
    [[app detailsPanel] toggleVisibility];
    [self updateOptionSegments];
}

- (IBAction)toggleDelta:(id)sender
{
    [table setDeltaValuesMode:![table deltaValuesMode]];
    [self updateOptionSegments];
}

- (IBAction)togglePowerMarker:(id)sender
{
    [table setPowerMarkerMode:![table powerMarkerMode]];
    [self updateOptionSegments];
}

- (IBAction)toggleQuicklookPanel:(id)sender
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

- (void)jobInProgress:(NSNotification *)aNotification
{
    [Dialogs showMessage:TR(@"A previous action is still hanging in there. You can't start a new one yet. Wait a few seconds, then try again.")];
}

- (void)jobStarted:(NSNotification *)aNotification
{
    [[self window] makeKeyAndOrderFront:nil];
    NSDictionary *ui = [aNotification userInfo];
    NSString *desc = [ui valueForKey:@"desc"];
    [[ProgressController mainProgressController] setJobDesc:desc];
    NSString *jobid = [ui valueForKey:@"jobid"];
    [[ProgressController mainProgressController] setJobId:jobid];
    [[ProgressController mainProgressController] showSheetForParent:[self window]];
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
