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
    table = [[ResultTable alloc] initWithPyParent:py view:matches];
    statsLabel = [[StatsLabel alloc] initWithPyParent:py labelView:stats];
    problemDialog = [[ProblemDialog alloc] initWithPy:py];
    [self initResultColumns];
    [self fillColumnsMenu];
    [matches setTarget:self];
    [matches setDoubleAction:@selector(openClicked:)];
    [table setDeltaColumns:[Utils array2IndexSet:[py deltaColumns]]];
    
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

- (NSString *)getScanErrorMessageForCode:(NSInteger)errorCode
{
    if (errorCode == 0) {
        return nil;
    }
    if (errorCode == 3) {
        return TR(@"NoScannableFileMsg");
    }
    return TR(@"UnknownErrorMsg");
}

/* Helpers */
- (void)fillColumnsMenu
{
    // The columns menu is supposed to be empty and initResultColumns must have been called
    for (NSTableColumn *col in _resultColumns)
    {
        NSMenuItem *mi = [columnsMenu addItemWithTitle:[[col headerCell] stringValue] action:@selector(toggleColumn:) keyEquivalent:@""];
        [mi setTag:[[col identifier] integerValue]];
        [mi setTarget:self];
        if ([[matches tableColumns] containsObject:col])
            [mi setState:NSOnState];
    }
    [columnsMenu addItem:[NSMenuItem separatorItem]];
    NSMenuItem *mi = [columnsMenu addItemWithTitle:TR(@"Reset to Default")
        action:@selector(resetColumnsToDefault:) keyEquivalent:@""];
    [mi setTarget:self];
}

- (NSTableColumn *)getColumnForIdentifier:(NSInteger)aIdentifier title:(NSString *)aTitle width:(NSInteger)aWidth refCol:(NSTableColumn *)aColumn
{
    NSNumber *n = [NSNumber numberWithInteger:aIdentifier];
    NSTableColumn *col = [[NSTableColumn alloc] initWithIdentifier:[n stringValue]];
    [col setWidth:aWidth];
    [col setEditable:NO];
    [[col dataCell] setFont:[[aColumn dataCell] font]];
    [[col headerCell] setStringValue:aTitle];
    [col setResizingMask:NSTableColumnUserResizingMask];
    [col setSortDescriptorPrototype:[[NSSortDescriptor alloc] initWithKey:[n stringValue] ascending:YES]];
    return col;
}

//Returns an array of identifiers, in order.
- (NSArray *)getColumnsOrder
{
    NSMutableArray *result = [NSMutableArray array];
    for (NSTableColumn *col in [matches tableColumns]) {
        NSString *colId = [col identifier];
        [result addObject:colId];
    }
    return result;
}

- (NSDictionary *)getColumnsWidth
{
    NSMutableDictionary *result = [NSMutableDictionary dictionary];
    for (NSTableColumn *col in [matches tableColumns]) {
        NSString *colId = [col identifier];
        NSNumber *width = [NSNumber numberWithDouble:[col width]];
        [result setObject:width forKey:colId];
    }
    return result;
}

- (void)restoreColumnsPosition:(NSArray *)aColumnsOrder widths:(NSDictionary *)aColumnsWidth
{
    for (NSMenuItem *mi in [columnsMenu itemArray]) {
        if ([mi state] == NSOnState) {
            [self toggleColumn:mi];
        }
    }
    //Add columns and set widths
    for (NSString *colId in aColumnsOrder) {
        NSInteger colIndex = [colId integerValue];
        if ((colIndex == 0) && (![colId isEqual:@"0"])) {
            continue;
        }
        NSTableColumn *col = [_resultColumns objectAtIndex:colIndex];
        NSNumber *width = [aColumnsWidth objectForKey:[col identifier]];
        NSMenuItem *mi = [columnsMenu itemWithTag:colIndex];
        if (width) {
            [col setWidth:[width floatValue]];
        }
        [self toggleColumn:mi];
    }
}

- (void)sendMarkedToTrash:(BOOL)hardlinkDeleted
{
    NSInteger mark_count = [[py getMarkCount] intValue];
    if (!mark_count) {
        return;
    }
    NSString *msg = TR(@"SendToTrashConfirmMsg");
    if (hardlinkDeleted) {
        msg = TR(@"HardlinkConfirmMsg");
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
    NSString *msg = [NSString stringWithFormat:TR(@"ClearIgnoreListConfirmMsg"),i];
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
    [op setTitle:TR(@"SelectCopyDestinationMsg")];
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
    NSString *exported = [py exportToXHTMLwithColumns:[self getColumnsOrder]];
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
    NSString *msg = [NSString stringWithFormat:TR(@"IgnoreConfirmMsg"),selectedDupeCount];
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
        [Dialogs showMessage:TR(@"NoCustomCommandMsg")];
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
    [op setTitle:TR(@"SelectMoveDestinationMsg")];
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
    // Virtual
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
    [sp setTitle:TR(@"SelectResultToSaveMsg")];
    if ([sp runModal] == NSOKButton) {
        [py saveResultsAs:[sp filename]];
        [[app recentResults] addFile:[sp filename]];
    }
}

- (IBAction)startDuplicateScan:(id)sender
{
    if ([py resultsAreModified]) {
        if ([Dialogs askYesNo:TR(@"ReallyWantToContinueMsg")] == NSAlertSecondButtonReturn) // NO
            return;
    }
    [self setScanOptions];
    NSInteger r = n2i([py doScan]);
    NSString *errorMsg = [self getScanErrorMessageForCode:r];
    if (errorMsg != nil) {
        [[ProgressController mainProgressController] hide];
        [Dialogs showMessage:errorMsg];
    }
}

- (IBAction)switchSelected:(id)sender
{
    [py makeSelectedReference];
}

- (IBAction)toggleColumn:(id)sender
{
    NSMenuItem *mi = sender;
    NSString *colId = [NSString stringWithFormat:@"%d",[mi tag]];
    NSTableColumn *col = [matches tableColumnWithIdentifier:colId];
    if (col == nil) {
        //Add Column
        col = [_resultColumns objectAtIndex:[mi tag]];
        [matches addTableColumn:col];
        [mi setState:NSOnState];
    }
    else {
        //Remove column
        [matches removeTableColumn:col];
        [mi setState:NSOffState];
    }
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

/* Notifications */
- (void)jobCompleted:(NSNotification *)aNotification
{
    id lastAction = [[ProgressController mainProgressController] jobId];
    if ([lastAction isEqualTo:jobCopy]) {
        if ([py scanWasProblematic]) {
            [problemDialog showWindow:self];
        }
        else {
            [Dialogs showMessage:TR(@"CopySuccessMsg")];
        }
    }
    else if ([lastAction isEqualTo:jobMove]) {
        if ([py scanWasProblematic]) {
            [problemDialog showWindow:self];
        }
        else {
            [Dialogs showMessage:TR(@"MoveSuccessMsg")];
        }
    }
    else if ([lastAction isEqualTo:jobDelete]) {
        if ([py scanWasProblematic]) {
            [problemDialog showWindow:self];
        }
        else {
            [Dialogs showMessage:TR(@"SendToTrashSuccessMsg")];
        }
    }
    else if ([lastAction isEqualTo:jobScan]) {
        NSInteger rowCount = [[table py] numberOfRows];
        if (rowCount == 0) {
            [Dialogs showMessage:TR(@"NoDuplicateFoundMsg")];
        }
    }
}

- (void)jobInProgress:(NSNotification *)aNotification
{
    [Dialogs showMessage:TR(@"TaskHangingMsg")];
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
