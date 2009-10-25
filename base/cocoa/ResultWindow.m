/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

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
    unsigned int flags = ( [theEvent modifierFlags] & 0x00FF );
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
    [self window];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(registrationRequired:) name:RegistrationRequired object:nil];
	[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobCompleted:) name:JobCompletedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobStarted:) name:JobStarted object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobInProgress:) name:JobInProgress object:nil];
	[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(resultsChanged:) name:ResultsChangedNotification object:nil];
	[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(resultsUpdated:) name:ResultsUpdatedNotification object:nil];
}

/* Helpers */
//Returns an array of identifiers, in order.
- (NSArray *)getColumnsOrder
{
    NSTableColumn *col;
    NSString *colId;
    NSMutableArray *result = [NSMutableArray array];
    NSEnumerator *e = [[matches tableColumns] objectEnumerator];
    while (col = [e nextObject])
    {
        colId = [col identifier];
        [result addObject:colId];
    }
    return result;
}

- (NSDictionary *)getColumnsWidth
{
    NSMutableDictionary *result = [NSMutableDictionary dictionary];
    NSTableColumn *col;
    NSString *colId;
    NSNumber *width;
    NSEnumerator *e = [[matches tableColumns] objectEnumerator];
    while (col = [e nextObject])
    {
        colId = [col identifier];
        width = [NSNumber numberWithFloat:[col width]];
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
    int i = [indexes firstIndex];
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
    NSEnumerator *e = [selected objectEnumerator];
    OVNode *node;
    while (node = [e nextObject])
        [r addObject:p2a([node indexPath])];
    return r;
}

- (void)updatePySelection
{
	NSArray *selection;
    if (_powerMode)
		selection = [py selectedPowerMarkerNodePaths];
    else
		selection = [py selectedResultNodePaths];
	[matches selectNodePaths:selection];
}

- (void)performPySelection:(NSArray *)aIndexPaths
{
    if (_powerMode)
        [py selectPowerMarkerNodePaths:aIndexPaths];
    else
        [py selectResultNodePaths:aIndexPaths];
}

- (void)refreshStats
{
    [stats setStringValue:[py getStatLine]];
}

/* Actions */
- (IBAction)changeDelta:(id)sender
{
    _displayDelta = [deltaSwitch selectedSegment] == 1;
    [py setDisplayDeltaValues:b2n(_displayDelta)];
    [matches reloadData];
    [self expandAll:nil];
}

- (IBAction)changePowerMarker:(id)sender
{
    _powerMode = [pmSwitch selectedSegment] == 1;
    if (_powerMode)
        [matches setTag:2];
    else
        [matches setTag:0];
    [self expandAll:nil];
    [self outlineView:matches didClickTableColumn:nil];
	[self updatePySelection];
}

- (IBAction)copyMarked:(id)sender
{
    int mark_count = [[py getMarkCount] intValue];
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
    int mark_count = [[py getMarkCount] intValue];
    if (!mark_count)
        return;
    if ([Dialogs askYesNo:[NSString stringWithFormat:@"You are about to send %d files to Trash. Continue?",mark_count]] == NSAlertSecondButtonReturn) // NO
        return;
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [py setRemoveEmptyFolders:[ud objectForKey:@"removeEmptyFolders"]];
    [py deleteMarked];
}

- (IBAction)expandAll:(id)sender
{
    for (int i=0;i < [matches numberOfRows];i++)
        [matches expandItem:[matches itemAtRow:i]];
}

- (IBAction)exportToXHTML:(id)sender
{
    NSString *exported = [py exportToXHTMLwithColumns:[self getColumnsOrder]];
    [[NSWorkspace sharedWorkspace] openFile:exported];
}

- (IBAction)moveMarked:(id)sender
{
    int mark_count = [[py getMarkCount] intValue];
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

- (IBAction)switchSelected:(id)sender
{
    // It might look like a complicated way to get the length of the current dupe list on the py side
    // but after a lot of fussing around, believe it or not, it actually is.
    int matchesTag = _powerMode ? 2 : 0;
    int startLen = [[py getOutlineView:matchesTag childCountsForPath:[NSArray array]] count];
    [self performPySelection:[self getSelectedPaths:YES]];
    [py makeSelectedReference];
    // In some cases (when in a filtered view in Power Marker mode, it's possible that the demoted
    // ref is not a part of the filter, making the table smaller. In those cases, we want to do a
    // complete reload of the table to avoid a crash.
    if ([[py getOutlineView:matchesTag childCountsForPath:[NSArray array]] count] == startLen)
        [[NSNotificationCenter defaultCenter] postNotificationName:ResultsUpdatedNotification object:self];
    else
        [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
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
    [matches reloadData];
    [self expandAll:nil];
}

/* Notifications */
- (void)windowWillClose:(NSNotification *)aNotification
{
    [NSApp hide:NSApp];
}

- (void)jobCompleted:(NSNotification *)aNotification
{
    [[NSNotificationCenter defaultCenter] postNotificationName:ResultsChangedNotification object:self];
    int r = n2i([py getOperationalErrorCount]);
    id lastAction = [[ProgressController mainProgressController] jobId];
    if ([lastAction isEqualTo:jobCopy])
    {
        if (r > 0)
            [Dialogs showMessage:[NSString stringWithFormat:@"%d file(s) couldn't be copied.",r]];
        else
            [Dialogs showMessage:@"All marked files were copied sucessfully."];
    }
    if ([lastAction isEqualTo:jobMove])
    {
        if (r > 0)
            [Dialogs showMessage:[NSString stringWithFormat:@"%d file(s) couldn't be moved. They were kept in the results, and still are marked.",r]];
        else
            [Dialogs showMessage:@"All marked files were moved sucessfully."];
    }
    if ([lastAction isEqualTo:jobDelete])
    {
        if (r > 0)
            [Dialogs showMessage:[NSString stringWithFormat:@"%d file(s) couldn't be sent to Trash. They were kept in the results, and still are marked.",r]];
        else
            [Dialogs showMessage:@"All marked files were sucessfully sent to Trash."];
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
    // NSLog(jobid);
    [[ProgressController mainProgressController] setJobId:jobid];
    [[ProgressController mainProgressController] showSheetForParent:[self window]];
}

- (void)registrationRequired:(NSNotification *)aNotification
{
    NSString *msg = @"This is a demo version, which only allows you 10 delete/copy/move actions per session. You cannot continue.";
    [Dialogs showMessage:msg];
}

- (void)resultsChanged:(NSNotification *)aNotification
{
    [matches reloadData];
    [self expandAll:nil];
    [self outlineViewSelectionDidChange:nil];
    [self refreshStats];
}

- (void)resultsUpdated:(NSNotification *)aNotification
{
	[matches invalidateBuffers];
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
