/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "ResultWindow.h"
#import "Dialogs.h"
#import "ProgressController.h"
#import "Utils.h"
#import "RegistrationInterface.h"
#import "AppDelegate.h"
#import "Consts.h"

@implementation MatchesView
- (void)keyDown:(NSEvent *)theEvent
{
    unichar key = [[theEvent charactersIgnoringModifiers] characterAtIndex:0];
    // get flags and strip the lower 16 (device dependant) bits
    NSUInteger flags = ( [theEvent modifierFlags] & 0x00FF );
    if (((key == NSDeleteFunctionKey) || (key == NSDeleteCharacter)) && (flags == 0))
        [self sendAction:@selector(removeSelected:) to:[self delegate]];
    else
    if ((key == 0x20) && (flags == 0)) // Space
        [self sendAction:@selector(markSelected:) to:[self delegate]];
    else
        [super keyDown:theEvent];
}
@end

@implementation ResultWindowBase
- (void)awakeFromNib
{
    _displayDelta = NO;
    _powerMode = NO;
    [self window];
    preferencesPanel = [[NSWindowController alloc] initWithWindowNibName:@"Preferences"];
    outline = [[ResultOutline alloc] initWithPyParent:py view:matches];
    [self initResultColumns];
    [self fillColumnsMenu];
    [deltaSwitch setSelectedSegment:0];
    [pmSwitch setSelectedSegment:0];
    [py setDisplayDeltaValues:b2n(_displayDelta)];
    [matches setTarget:self];
    [matches setDoubleAction:@selector(openClicked:)];
    [self refreshStats];
    
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(registrationRequired:) name:RegistrationRequired object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobCompleted:) name:JobCompletedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobStarted:) name:JobStarted object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobInProgress:) name:JobInProgress object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(resultsMarkingChanged:) name:ResultsMarkingChangedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(resultsChanged:) name:ResultsChangedNotification object:nil];
}

- (void)dealloc
{
    [outline release];
    [preferencesPanel release];
    [super dealloc];
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
    NSMenuItem *mi = [columnsMenu addItemWithTitle:@"Reset to Default" action:@selector(resetColumnsToDefault:) keyEquivalent:@""];
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

- (NSArray *)getSelectedPaths:(BOOL)aDupesOnly
{
    if (_powerMode)
        aDupesOnly = NO;
    NSIndexSet *indexes = [matches selectedRowIndexes];
    NSMutableArray *nodeList = [NSMutableArray array];
    NSInteger i = [indexes firstIndex];
    while (i != NSNotFound) {
        NSIndexPath *path = [matches itemAtRow:i];
        if (!aDupesOnly || ([path length] > 1))
            [nodeList addObject:p2a(path)];
        i = [indexes indexGreaterThanIndex:i];
    }
    return nodeList;
}

- (void)initResultColumns
{
    // Virtual
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
        if ([colId isEqual:@"mark"]) {
            continue;
        }
        NSTableColumn *col = [_resultColumns objectAtIndex:[colId intValue]];
        NSNumber *width = [aColumnsWidth objectForKey:[col identifier]];
        NSMenuItem *mi = [columnsMenu itemWithTag:[colId intValue]];
        if (width) {
            [col setWidth:[width floatValue]];
        }
        [self toggleColumn:mi];
    }
}

// - (void)updatePySelection
// {
//     NSArray *selection;
//     if (_powerMode) {
//         selection = [py selectedPowerMarkerNodePaths];
//     }
//     else {
//         selection = [py selectedResultNodePaths];
//     }
//     [matches selectNodePaths:selection];
// }

- (void)performPySelection:(NSArray *)aIndexPaths
{
    if (_powerMode) {
        [py selectPowerMarkerNodePaths:aIndexPaths];
    }
    else {
        [py selectResultNodePaths:aIndexPaths];
    }
}

- (void)refreshStats
{
    [stats setStringValue:[py getStatLine]];
}

/* Reload the matches outline and restore selection from py */
- (void)reloadMatches
{
    [outline refresh];
}

/* Actions */
- (IBAction)clearIgnoreList:(id)sender
{
    NSInteger i = n2i([py getIgnoreListCount]);
    if (!i)
        return;
    if ([Dialogs askYesNo:[NSString stringWithFormat:@"Do you really want to remove all %d items from the ignore list?",i]] == NSAlertSecondButtonReturn) // NO
        return;
    [py clearIgnoreList];
}

- (IBAction)changeDelta:(id)sender
{
    _displayDelta = [deltaSwitch selectedSegment] == 1;
    [py setDisplayDeltaValues:b2n(_displayDelta)];
    [self reloadMatches];
}

- (IBAction)changePowerMarker:(id)sender
{
    _powerMode = [pmSwitch selectedSegment] == 1;
    [outline setPowerMarkerMode:_powerMode];
    // [self outlineView:matches didClickTableColumn:nil];
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
    [op setTitle:@"Select a directory to copy marked files to"];
    if ([op runModalForTypes:nil] == NSOKButton)
    {
        NSString *directory = [[op filenames] objectAtIndex:0];
        NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
        [py copyOrMove:b2n(YES) markedTo:directory recreatePath:[ud objectForKey:@"recreatePathType"]];
    }
}

- (IBAction)deleteMarked:(id)sender
{
    NSInteger mark_count = [[py getMarkCount] intValue];
    if (!mark_count)
        return;
    if ([Dialogs askYesNo:[NSString stringWithFormat:@"You are about to send %d files to Trash. Continue?",mark_count]] == NSAlertSecondButtonReturn) // NO
        return;
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [py setRemoveEmptyFolders:[ud objectForKey:@"removeEmptyFolders"]];
    [py deleteMarked];
}

- (IBAction)exportToXHTML:(id)sender
{
    NSString *exported = [py exportToXHTMLwithColumns:[self getColumnsOrder]];
    [[NSWorkspace sharedWorkspace] openFile:exported];
}

- (IBAction)filter:(id)sender
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [py setEscapeFilterRegexp:b2n(!n2b([ud objectForKey:@"useRegexpFilter"]))];
    [py applyFilter:[filterField stringValue]];
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
}

- (IBAction)ignoreSelected:(id)sender
{
    NSArray *pathList = [self getSelectedPaths:YES];
    if (![pathList count])
        return;
    NSString *msg = [NSString stringWithFormat:@"All selected %d matches are going to be ignored in all subsequent scans. Continue?",[pathList count]];
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [py addSelectedToIgnoreList];
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
}

- (IBAction)markAll:(id)sender
{
    [py markAll];
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsMarkingChangedNotification object:self];
}

- (IBAction)markInvert:(id)sender
{
    [py markInvert];
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsMarkingChangedNotification object:self];
}

- (IBAction)markNone:(id)sender
{
    [py markNone];
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsMarkingChangedNotification object:self];
}

- (IBAction)markSelected:(id)sender
{
    [self performPySelection:[self getSelectedPaths:YES]];
    [py toggleSelectedMark];
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsMarkingChangedNotification object:self];
}

- (IBAction)markToggle:(id)sender
{
    NSIndexPath *path = [matches itemAtRow:[matches clickedRow]];
    [self performPySelection:[NSArray arrayWithObject:p2a(path)]];
    [py toggleSelectedMark];
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsMarkingChangedNotification object:self];
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
    [op setTitle:@"Select a directory to move marked files to"];
    if ([op runModalForTypes:nil] == NSOKButton)
    {
        NSString *directory = [[op filenames] objectAtIndex:0];
        NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
        [py setRemoveEmptyFolders:[ud objectForKey:@"removeEmptyFolders"]];
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
    [self performPySelection:[self getSelectedPaths:NO]];
    [py openSelected];
}

- (IBAction)refresh:(id)sender
{
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
}

- (IBAction)removeMarked:(id)sender
{
    int mark_count = [[py getMarkCount] intValue];
    if (!mark_count)
        return;
    if ([Dialogs askYesNo:[NSString stringWithFormat:@"You are about to remove %d files from results. Continue?",mark_count]] == NSAlertSecondButtonReturn) // NO
        return;
    [py removeMarked];
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
}

- (IBAction)removeSelected:(id)sender
{
    NSArray *pathList = [self getSelectedPaths:YES];
    if (![pathList count])
        return;
    if ([Dialogs askYesNo:[NSString stringWithFormat:@"You are about to remove %d files from results. Continue?",[pathList count]]] == NSAlertSecondButtonReturn) // NO
        return;
    [self performPySelection:[self getSelectedPaths:YES]];
    [py removeSelected];
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
}

- (IBAction)renameSelected:(id)sender
{
    NSInteger col = [matches columnWithIdentifier:@"0"];
    NSInteger row = [matches selectedRow];
    [matches editColumn:col row:row withEvent:[NSApp currentEvent] select:YES];
}

- (IBAction)resetColumnsToDefault:(id)sender
{
    // Virtual
}

- (IBAction)revealSelected:(id)sender
{
    [self performPySelection:[self getSelectedPaths:NO]];
    [py revealSelected];
}

- (IBAction)showPreferencesPanel:(id)sender
{
    [preferencesPanel showWindow:sender];
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
    if (col == nil)
    {
        //Add Column
        col = [_resultColumns objectAtIndex:[mi tag]];
        [matches addTableColumn:col];
        [mi setState:NSOnState];
    }
    else
    {
        //Remove column
        [matches removeTableColumn:col];
        [mi setState:NSOffState];
    }
}

- (IBAction)toggleDelta:(id)sender
{
    if ([deltaSwitch selectedSegment] == 1)
        [deltaSwitch setSelectedSegment:0];
    else
        [deltaSwitch setSelectedSegment:1];
    [self changeDelta:sender];
}

- (IBAction)toggleDetailsPanel:(id)sender
{
    [[(AppDelegateBase *)app detailsPanel] toggleVisibility];
}

- (IBAction)togglePowerMarker:(id)sender
{
    if ([pmSwitch selectedSegment] == 1)
        [pmSwitch setSelectedSegment:0];
    else
        [pmSwitch setSelectedSegment:1];
    [self changePowerMarker:sender];
}

/* Notifications */
- (void)windowWillClose:(NSNotification *)aNotification
{
    [NSApp hide:NSApp];
}

- (void)jobCompleted:(NSNotification *)aNotification
{
    NSInteger r = n2i([py getOperationalErrorCount]);
    id lastAction = [[ProgressController mainProgressController] jobId];
    if ([lastAction isEqualTo:jobCopy]) {
        if (r > 0)
            [Dialogs showMessage:[NSString stringWithFormat:@"%d file(s) couldn't be copied.",r]];
        else
            [Dialogs showMessage:@"All marked files were copied sucessfully."];
    }
    else if ([lastAction isEqualTo:jobMove]) {
        if (r > 0)
            [Dialogs showMessage:[NSString stringWithFormat:@"%d file(s) couldn't be moved. They were kept in the results, and still are marked.",r]];
        else
            [Dialogs showMessage:@"All marked files were moved sucessfully."];
    }
    else if ([lastAction isEqualTo:jobDelete]) {
        if (r > 0) {
            NSString *msg = @"%d file(s) couldn't be sent to Trash. They were kept in the results, "\
                "and still are marked. See the F.A.Q. section in the help file for details.";
            [Dialogs showMessage:[NSString stringWithFormat:msg,r]];
        }
        else
            [Dialogs showMessage:@"All marked files were sucessfully sent to Trash."];
    }
    else if ([lastAction isEqualTo:jobScan]) {
        NSInteger groupCount = [outline intProperty:@"children_count" valueAtPath:nil];
        if (groupCount == 0)
            [Dialogs showMessage:@"No duplicates found."];
    }
    
    // Re-activate toolbar items right after the progress bar stops showing instead of waiting until
    // a mouse-over is performed
    [[[self window] toolbar] validateVisibleItems];
}

- (void)jobInProgress:(NSNotification *)aNotification
{
    [Dialogs showMessage:@"A previous action is still hanging in there. You can't start a new one yet. Wait a few seconds, then try again."];
}

- (void)jobStarted:(NSNotification *)aNotification
{
    NSDictionary *ui = [aNotification userInfo];
    NSString *desc = [ui valueForKey:@"desc"];
    [[ProgressController mainProgressController] setJobDesc:desc];
    NSString *jobid = [ui valueForKey:@"jobid"];
    [[ProgressController mainProgressController] setJobId:jobid];
    [[ProgressController mainProgressController] showSheetForParent:[self window]];
}

- (void)registrationRequired:(NSNotification *)aNotification
{
    NSString *msg = @"This is a demo version, which only allows you 10 delete/copy/move actions per session. You cannot continue.";
    [Dialogs showMessage:msg];
}

- (void)outlineViewSelectionDidChange:(NSNotification *)notification
{
    [self performPySelection:[self getSelectedPaths:NO]];
}

- (void)resultsChanged:(NSNotification *)aNotification
{
    [self refreshStats];
}

- (void)resultsMarkingChanged:(NSNotification *)aNotification
{
    [self refreshStats];
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
