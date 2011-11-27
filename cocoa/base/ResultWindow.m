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
    py = [app py];
    [[self window] setTitle:fmt(@"%@ Results", [py appName])];
    columnsMenu = [app columnsMenu];
    /* Put a cute iTunes-like bottom bar */
    [[self window] setContentBorderThickness:28 forEdge:NSMinYEdge];
    table = [[ResultTable alloc] initWithPy:[py resultTable] view:matches];
    statsLabel = [[StatsLabel alloc] initWithPyParent:py labelView:stats];
    problemDialog = [[ProblemDialog alloc] initWithPy:py];
    [self initResultColumns];
    [self fillColumnsMenu];
    [matches setTarget:self];
    [matches setDoubleAction:@selector(openClicked:)];
    [table setDeltaColumns:[NSSet setWithArray:[py deltaColumns]]];
    
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobCompleted:) name:JobCompletedNotification object:nil];
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
    NSArray *menuItems = [[[table columns] py] menuItems];
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
    NSInteger mark_count = [[py getMarkCount] intValue];
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
    [py setRemoveEmptyFolders:n2b([ud objectForKey:@"removeEmptyFolders"])];
    if (hardlinkDeleted) {
        [py hardlinkMarked];
    }
    else {
        [py deleteMarked];
    }
}

- (void)updateOptionSegments
{
    [optionsSwitch setSelected:[[app detailsPanel] isVisible] forSegment:0];
    [optionsSwitch setSelected:[table powerMarkerMode] forSegment:1];
    [optionsSwitch setSelected:[table deltaValuesMode] forSegment:2];
}

/* Actions */
- (IBAction)clearIgnoreList:(id)sender
{
    NSInteger i = n2i([py getIgnoreListCount]);
    if (!i)
        return;
    NSString *msg = [NSString stringWithFormat:TR(@"Do you really want to remove all %d items from the ignore list?"),i];
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [py clearIgnoreList];
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
    NSInteger mark_count = [[py getMarkCount] intValue];
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
        [py copyOrMove:b2n(YES) markedTo:directory recreatePath:[ud objectForKey:@"recreatePathType"]];
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
    NSString *exported = [py exportToXHTML];
    [[NSWorkspace sharedWorkspace] openFile:exported];
}

- (IBAction)filter:(id)sender
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [py setEscapeFilterRegexp:!n2b([ud objectForKey:@"useRegexpFilter"])];
    [py applyFilter:[filterField stringValue]];
}

- (IBAction)ignoreSelected:(id)sender
{
    NSInteger selectedDupeCount = [table selectedDupeCount];
    if (!selectedDupeCount)
        return;
    NSString *msg = [NSString stringWithFormat:TR(@"All selected %d matches are going to be ignored in all subsequent scans. Continue?"),selectedDupeCount];
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [py addSelectedToIgnoreList];
}

- (IBAction)invokeCustomCommand:(id)sender
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSString *cmd = [ud stringForKey:@"CustomCommand"];
    if ((cmd != nil) && ([cmd length] > 0)) {
        [py invokeCommand:cmd];
    }
    else {
        [Dialogs showMessage:TR(@"You have no custom command set up. Set it up in your preferences.")];
    }
}

- (IBAction)markAll:(id)sender
{
    [py markAll];
}

- (IBAction)markInvert:(id)sender
{
    [py markInvert];
}

- (IBAction)markNone:(id)sender
{
    [py markNone];
}

- (IBAction)markSelected:(id)sender
{
    [py toggleSelectedMark];
}

- (IBAction)moveMarked:(id)sender
{
    NSInteger mark_count = [[py getMarkCount] intValue];
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
        [py setRemoveEmptyFolders:n2b([ud objectForKey:@"removeEmptyFolders"])];
        [py copyOrMove:b2n(NO) markedTo:directory recreatePath:[ud objectForKey:@"recreatePathType"]];
    }
}

- (IBAction)openClicked:(id)sender
{
    if ([matches clickedRow] < 0) {
        return;
    }
    [matches selectRowIndexes:[NSIndexSet indexSetWithIndex:[matches clickedRow]] byExtendingSelection:NO];
    [py openSelected];
}

- (IBAction)openSelected:(id)sender
{
    [py openSelected];
}

- (IBAction)removeMarked:(id)sender
{
    int mark_count = [[py getMarkCount] intValue];
    if (!mark_count)
        return;
    NSString *msg = [NSString stringWithFormat:@"You are about to remove %d files from results. Continue?",mark_count];
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [py removeMarked];
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
    PrioritizeDialog *dlg = [[PrioritizeDialog alloc] initWithPy:py];
    NSInteger result = [NSApp runModalForWindow:[dlg window]];
    if (result == NSRunStoppedResponse) {
        [[dlg py] performReprioritization];
    }
    [dlg release];
    [[self window] makeKeyAndOrderFront:nil];
}

- (IBAction)resetColumnsToDefault:(id)sender
{
    [[[table columns] py] resetToDefaults];
}

- (IBAction)revealSelected:(id)sender
{
    [py revealSelected];
}

- (IBAction)saveResults:(id)sender
{
    NSSavePanel *sp = [NSSavePanel savePanel];
    [sp setCanCreateDirectories:YES];
    [sp setAllowedFileTypes:[NSArray arrayWithObject:@"dupeguru"]];
    [sp setTitle:TR(@"Select a file to save your results to")];
    if ([sp runModal] == NSOKButton) {
        [py saveResultsAs:[sp filename]];
        [[app recentResults] addFile:[sp filename]];
    }
}

- (IBAction)startDuplicateScan:(id)sender
{
    if ([py resultsAreModified]) {
        if ([Dialogs askYesNo:TR(@"You have unsaved results, do you really want to continue?")] == NSAlertSecondButtonReturn) // NO
            return;
    }
    [self setScanOptions];
    [py doScan];
}

- (IBAction)switchSelected:(id)sender
{
    [py makeSelectedReference];
}

- (IBAction)toggleColumn:(id)sender
{
    NSMenuItem *mi = sender;
    BOOL checked = [[[table columns] py] toggleMenuItem:[mi tag]];
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

/* Notifications */
- (void)jobCompleted:(NSNotification *)aNotification
{
    id lastAction = [[ProgressController mainProgressController] jobId];
    if ([lastAction isEqualTo:jobCopy]) {
        if ([py scanWasProblematic]) {
            [problemDialog showWindow:self];
        }
        else {
            [Dialogs showMessage:TR(@"All marked files were copied sucessfully.")];
        }
    }
    else if ([lastAction isEqualTo:jobMove]) {
        if ([py scanWasProblematic]) {
            [problemDialog showWindow:self];
        }
        else {
            [Dialogs showMessage:TR(@"All marked files were moved sucessfully.")];
        }
    }
    else if ([lastAction isEqualTo:jobDelete]) {
        if ([py scanWasProblematic]) {
            [problemDialog showWindow:self];
        }
        else {
            [Dialogs showMessage:TR(@"All marked files were sucessfully sent to Trash.")];
        }
    }
    else if ([lastAction isEqualTo:jobScan]) {
        NSInteger rowCount = [[table py] numberOfRows];
        if (rowCount == 0) {
            [Dialogs showMessage:TR(@"No duplicates found.")];
        }
    }
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
