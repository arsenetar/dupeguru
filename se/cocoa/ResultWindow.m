/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "ResultWindow.h"
#import "cocoalib/Dialogs.h"
#import "cocoalib/ProgressController.h"
#import "cocoalib/Utils.h"
#import "AppDelegate.h"
#import "Consts.h"

@implementation ResultWindow
/* Override */
- (void)awakeFromNib
{
    [super awakeFromNib];
    _detailsPanel = nil;
    _displayDelta = NO;
    _powerMode = NO;
    _deltaColumns = [[NSMutableIndexSet indexSetWithIndexesInRange:NSMakeRange(2,4)] retain];
    [_deltaColumns removeIndex:3];
    [deltaSwitch setSelectedSegment:0];
    [pmSwitch setSelectedSegment:0];
    [py setDisplayDeltaValues:b2n(_displayDelta)];
    [matches setTarget:self];
    [matches setDoubleAction:@selector(openSelected:)];
    [[actionMenu itemAtIndex:0] setImage:[NSImage imageNamed: @"gear"]];
    [self initResultColumns];
    [self refreshStats];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(resultsMarkingChanged:) name:ResultsMarkingChangedNotification object:nil];
    
    NSToolbar *t = [[[NSToolbar alloc] initWithIdentifier:@"ResultWindowToolbar"] autorelease];
    [t setAllowsUserCustomization:YES];
    [t setAutosavesConfiguration:YES];
    [t setDisplayMode:NSToolbarDisplayModeIconAndLabel];
    [t setDelegate:self];
    [[self window] setToolbar:t];
}

/* Override */
- (NSString *)logoImageName
{
    return @"dgse_logo_32";
}

/* Actions */
- (IBAction)clearIgnoreList:(id)sender
{
    int i = n2i([py getIgnoreListCount]);
    if (!i)
        return;
    if ([Dialogs askYesNo:[NSString stringWithFormat:@"Do you really want to remove all %d items from the ignore list?",i]] == NSAlertSecondButtonReturn) // NO
        return;
    [py clearIgnoreList];
}

- (IBAction)exportToXHTML:(id)sender
{
    NSString *xsltPath = [[NSBundle mainBundle] pathForResource:@"dg" ofType:@"xsl"];
    NSString *cssPath = [[NSBundle mainBundle] pathForResource:@"hardcoded" ofType:@"css"];
    NSString *exported = [py exportToXHTMLwithColumns:[self getColumnsOrder] xslt:xsltPath css:cssPath];
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
    if ([Dialogs askYesNo:[NSString stringWithFormat:@"All selected %d matches are going to be ignored in all subsequent scans. Continue?",[nodeList count]]] == NSAlertSecondButtonReturn) // NO
        return;
    [self performPySelection:[self getSelectedPaths:YES]];
    [py addSelectedToIgnoreList];
    [py removeSelected];
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
    int col = [matches columnWithIdentifier:@"0"];
    int row = [matches selectedRow];
    [matches editColumn:col row:row withEvent:[NSApp currentEvent] select:YES];
}

- (IBAction)resetColumnsToDefault:(id)sender
{
    NSMutableArray *columnsOrder = [NSMutableArray array];
    [columnsOrder addObject:@"0"];
    [columnsOrder addObject:@"1"];
    [columnsOrder addObject:@"2"];
    [columnsOrder addObject:@"6"];
    NSMutableDictionary *columnsWidth = [NSMutableDictionary dictionary];
    [columnsWidth setObject:i2n(195) forKey:@"0"];
    [columnsWidth setObject:i2n(120) forKey:@"1"];
    [columnsWidth setObject:i2n(63) forKey:@"2"];
    [columnsWidth setObject:i2n(60) forKey:@"6"];
    [self restoreColumnsPosition:columnsOrder widths:columnsWidth];
}

- (IBAction)revealSelected:(id)sender
{
    [self performPySelection:[self getSelectedPaths:NO]];
    [py revealSelected];
}

- (IBAction)showPreferencesPanel:(id)sender
{
    [preferencesPanel makeKeyAndOrderFront:sender];
}

- (IBAction)startDuplicateScan:(id)sender
{
    if ([matches numberOfRows] > 0)
    {
        if ([Dialogs askYesNo:@"Are you sure you want to start a new duplicate scan?"] == NSAlertSecondButtonReturn) // NO
            return;
    }
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    PyDupeGuru *_py = (PyDupeGuru *)py;
    [_py setScanType:[ud objectForKey:@"scanType"]];
    [_py setMinMatchPercentage:[ud objectForKey:@"minMatchPercentage"]];
    [_py setWordWeighting:[ud objectForKey:@"wordWeighting"]];
    [_py setMixFileKind:[ud objectForKey:@"mixFileKind"]];
    [_py setMatchSimilarWords:[ud objectForKey:@"matchSimilarWords"]];
    int smallFileThreshold = [ud integerForKey:@"smallFileThreshold"]; // In KB
    int sizeThreshold = [ud boolForKey:@"ignoreSmallFiles"] ? smallFileThreshold * 1024 : 0; // The py side wants bytes
    [_py setSizeThreshold:sizeThreshold];
    int r = n2i([py doScan]);
    [matches reloadData];
    [self refreshStats];
    if (r != 0)
        [[ProgressController mainProgressController] hide];
    if (r == 1)
        [Dialogs showMessage:@"You cannot make a duplicate scan with only reference directories."];
    if (r == 3)
    {
        [Dialogs showMessage:@"The selected directories contain no scannable file."];
        [app toggleDirectories:nil];
    }

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
    if (!_detailsPanel)
        _detailsPanel = [[DetailsPanel alloc] initWithPy:py];
    if ([[_detailsPanel window] isVisible])
        [[_detailsPanel window] close];
    else
        [[_detailsPanel window] orderFront:nil];
}

/* Public */
- (NSTableColumn *)getColumnForIdentifier:(int)aIdentifier title:(NSString *)aTitle width:(int)aWidth refCol:(NSTableColumn *)aColumn
{
    NSNumber *n = [NSNumber numberWithInt:aIdentifier];
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

- (void)initResultColumns
{
    NSTableColumn *refCol = [matches tableColumnWithIdentifier:@"0"];
    _resultColumns = [[NSMutableArray alloc] init];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"0"]]; // File Name
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"1"]]; // Directory
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"2"]]; // Size
    [_resultColumns addObject:[self getColumnForIdentifier:3 title:@"Kind" width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:4 title:@"Creation" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:5 title:@"Modification" width:120 refCol:refCol]];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"6"]]; // Match %
    [_resultColumns addObject:[self getColumnForIdentifier:7 title:@"Words Used" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:8 title:@"Dupe Count" width:80 refCol:refCol]];
}

- (void)restoreColumnsPosition:(NSArray *)aColumnsOrder widths:(NSDictionary *)aColumnsWidth
{
    NSTableColumn *col;
    NSString *colId;
    NSNumber *width;
    NSMenuItem *mi;
    //Remove all columns
    NSEnumerator *e = [[columnsMenu itemArray] objectEnumerator];
    while (mi = [e nextObject])
    {
        if ([mi state] == NSOnState)
            [self toggleColumn:mi];
    }
    //Add columns and set widths
    e = [aColumnsOrder objectEnumerator];
    while (colId = [e nextObject])
    {
        if (![colId isEqual:@"mark"])
        {
            col = [_resultColumns objectAtIndex:[colId intValue]];
            width = [aColumnsWidth objectForKey:[col identifier]];
            mi = [columnsMenu itemWithTag:[colId intValue]];
            if (width)
                [col setWidth:[width floatValue]];
            [self toggleColumn:mi];
        }
    }
}

/* Delegate */
- (void)outlineView:(NSOutlineView *)outlineView willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)tableColumn item:(id)item
{ 
    OVNode *node = item;
    if ([[tableColumn identifier] isEqual:@"mark"])
    {
        [cell setEnabled: [node isMarkable]];
    }
    if ([cell isKindOfClass:[NSTextFieldCell class]])
    {
        // Determine if the text color will be blue due to directory being reference.
        NSTextFieldCell *textCell = cell;
        if ([node isMarkable])
            [textCell setTextColor:[NSColor blackColor]];
        else
            [textCell setTextColor:[NSColor blueColor]];
        if ((_displayDelta) && (_powerMode || ([node level] > 1)))
        {
            int i = [[tableColumn identifier] intValue];
            if ([_deltaColumns containsIndex:i])
                [textCell setTextColor:[NSColor orangeColor]];
        }
    }
}

/* Notifications */
- (void)outlineViewSelectionDidChange:(NSNotification *)notification
{
    [self performPySelection:[self getSelectedPaths:NO]];
    [py refreshDetailsWithSelected];
    [[NSNotificationCenter defaultCenter] postNotificationName:DuplicateSelectionChangedNotification object:self];
}

- (void)resultsMarkingChanged:(NSNotification *)aNotification
{
    [matches invalidateMarkings];
    [self refreshStats];
}
@end
