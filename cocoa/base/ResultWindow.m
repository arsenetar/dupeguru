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

- (void)outlineView:(NSOutlineView *)outlineView setObjectValue:(id)object forTableColumn:(NSTableColumn *)tableColumn byItem:(id)item
{
    if (![[tableColumn identifier] isEqual:@"0"])
        return; //We only want to cover renames.
    OVNode *node = item;
    NSString *oldName = [[node buffer] objectAtIndex:0];
    NSString *newName = object;
    if (![newName isEqual:oldName])
    {
        BOOL renamed = n2b([(PyDupeGuruBase *)py renameSelected:newName]);
        if (renamed)
            [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
        else
            [Dialogs showMessage:[NSString stringWithFormat:@"The name '%@' already exists.",newName]];
    }
}
@end

@implementation ResultWindowBase
- (void)awakeFromNib
{
    _displayDelta = NO;
    _powerMode = NO;
    [self window];
    preferencesPanel = [[NSWindowController alloc] initWithWindowNibName:@"Preferences"];
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
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(resultsUpdated:) name:ResultsUpdatedNotification object:nil];
}

- (void)dealloc
{
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

- (NSArray *)getSelected:(BOOL)aDupesOnly
{
    if (_powerMode)
        aDupesOnly = NO;
    NSIndexSet *indexes = [matches selectedRowIndexes];
    NSMutableArray *nodeList = [NSMutableArray array];
    OVNode *node;
    NSInteger i = [indexes firstIndex];
    while (i != NSNotFound)
    {
        node = [matches itemAtRow:i];
        if (!aDupesOnly || ([node level] > 1))
            [nodeList addObject:node];
        i = [indexes indexGreaterThanIndex:i];
    }
    return nodeList;
}

- (NSArray *)getSelectedPaths:(BOOL)aDupesOnly
{
    NSMutableArray *r = [NSMutableArray array];
    NSArray *selected = [self getSelected:aDupesOnly];
    for (OVNode *node in selected) {
        [r addObject:p2a([node indexPath])];
    }
    return r;
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

- (void)updatePySelection
{
    NSArray *selection;
    if (_powerMode) {
        selection = [py selectedPowerMarkerNodePaths];
    }
    else {
        selection = [py selectedResultNodePaths];
    }
    [matches selectNodePaths:selection];
}

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
    [matches setDelegate:nil];
    [matches reloadData];
    [matches expandItem:nil expandChildren:YES];
    [matches setDelegate:self];
    [self updatePySelection];
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
    if (_powerMode)
        [matches setTag:2];
    else
        [matches setTag:0];
    [matches expandItem:nil expandChildren:YES];
    [self outlineView:matches didClickTableColumn:nil];
    [self updatePySelection];
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
    NSArray *nodeList = [self getSelected:YES];
    if (![nodeList count])
        return;
    NSString *msg = [NSString stringWithFormat:@"All selected %d matches are going to be ignored in all subsequent scans. Continue?",[nodeList count]];
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
    OVNode *node = [matches itemAtRow:[matches clickedRow]];
    [self performPySelection:[NSArray arrayWithObject:p2a([node indexPath])]];
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
    NSArray *nodeList = [self getSelected:YES];
    if (![nodeList count])
        return;
    if ([Dialogs askYesNo:[NSString stringWithFormat:@"You are about to remove %d files from results. Continue?",[nodeList count]]] == NSAlertSecondButtonReturn) // NO
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
    // It might look like a complicated way to get the length of the current dupe list on the py side
    // but after a lot of fussing around, believe it or not, it actually is.
    NSInteger matchesTag = _powerMode ? 2 : 0;
    NSInteger startLen = [[py getOutlineView:matchesTag childCountsForPath:[NSArray array]] count];
    [py makeSelectedReference];
    [self performPySelection:[self getSelectedPaths:NO]];
    // In some cases (when in a filtered view in Power Marker mode, it's possible that the demoted
    // ref is not a part of the filter, making the table smaller. In those cases, we want to do a
    // complete reload of the table to avoid a crash.
    if ([[py getOutlineView:matchesTag childCountsForPath:[NSArray array]] count] == startLen)
        [[NSNotificationCenter defaultCenter] postNotificationName:ResultsUpdatedNotification object:self];
    else
        [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
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

/* Delegate */
- (void)outlineView:(NSOutlineView *)outlineView didClickTableColumn:(NSTableColumn *)tableColumn
{
    if ([[outlineView sortDescriptors] count] < 1)
        return;
    NSSortDescriptor *sd = [[outlineView sortDescriptors] objectAtIndex:0];
    if (_powerMode)
        [py sortDupesBy:i2n([[sd key] intValue]) ascending:b2n([sd ascending])];
    else
        [py sortGroupsBy:i2n([[sd key] intValue]) ascending:b2n([sd ascending])];
    [self reloadMatches];
}

- (void)outlineView:(NSOutlineView *)outlineView willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)tableColumn item:(id)item
{ 
    OVNode *node = item;
    if ([[tableColumn identifier] isEqual:@"mark"]) {
        [cell setEnabled: [node isMarkable]];
    }
    if ([cell isKindOfClass:[NSTextFieldCell class]]) {
        // Determine if the text color will be blue due to directory being reference.
        NSTextFieldCell *textCell = cell;
        if ([node isMarkable]) {
            [textCell setTextColor:[NSColor blackColor]];
        }
        else {
            [textCell setTextColor:[NSColor blueColor]];
        }
        if ((_displayDelta) && (_powerMode || ([node level] > 1))) {
            NSInteger i = [[tableColumn identifier] integerValue];
            if ([_deltaColumns containsIndex:i]) {
                [textCell setTextColor:[NSColor orangeColor]];
            }
        }
    }
}

/* Notifications */
- (void)windowWillClose:(NSNotification *)aNotification
{
    [NSApp hide:NSApp];
}

- (void)jobCompleted:(NSNotification *)aNotification
{
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
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
        NSInteger groupCount = [[py getOutlineView:0 childCountsForPath:[NSArray array]] count];
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
    [self reloadMatches];
    [self refreshStats];
}

- (void)resultsMarkingChanged:(NSNotification *)aNotification
{
    [matches invalidateMarkings];
    [self refreshStats];
}

- (void)resultsUpdated:(NSNotification *)aNotification
{
    [matches invalidateBuffers];
    [matches invalidateMarkings];
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
