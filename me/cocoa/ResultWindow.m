#import "ResultWindow.h"
#import "cocoalib/Dialogs.h"
#import "cocoalib/ProgressController.h"
#import "cocoalib/RegistrationInterface.h"
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
    _deltaColumns = [[NSMutableIndexSet indexSetWithIndexesInRange:NSMakeRange(2,7)] retain];
    [_deltaColumns removeIndex:6];
    [deltaSwitch setSelectedSegment:0];
    [pmSwitch setSelectedSegment:0];
    [py setDisplayDeltaValues:b2n(_displayDelta)];
    [matches setTarget:self];
    [matches setDoubleAction:@selector(openSelected:)];
    [[actionMenu itemAtIndex:0] setImage:[NSImage imageNamed: @"gear"]];
    [self initResultColumns];
    [self refreshStats];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(resultsMarkingChanged:) name:ResultsMarkingChangedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(duplicateSelectionChanged:) name:DuplicateSelectionChangedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(resultsChanged:) name:ResultsChangedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobCompleted:) name:JobCompletedNotification object:nil];
    
    NSToolbar *t = [[[NSToolbar alloc] initWithIdentifier:@"ResultWindowToolbar"] autorelease];
    [t setAllowsUserCustomization:YES];
    [t setAutosavesConfiguration:YES];
    [t setDisplayMode:NSToolbarDisplayModeIconAndLabel];
    [t setDelegate:self];
    [[self window] setToolbar:t];
}

/* Overrides */
- (NSString *)logoImageName
{
    return @"dgme_logo32";
}

/* Actions */

- (IBAction)changePowerMarker:(id)sender
{
    _powerMode = [pmSwitch selectedSegment] == 1;
    if (_powerMode)
        [matches setTag:2];
    else
        [matches setTag:0];
    [self expandAll:nil];
    [self outlineView:matches didClickTableColumn:nil];
}

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

- (IBAction)removeDeadTracks:(id)sender
{
    [(PyDupeGuru *)py scanDeadTracks];
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
    [columnsOrder addObject:@"2"];
    [columnsOrder addObject:@"3"];
    [columnsOrder addObject:@"4"];
    [columnsOrder addObject:@"16"];
    NSMutableDictionary *columnsWidth = [NSMutableDictionary dictionary];
    [columnsWidth setObject:i2n(214) forKey:@"0"];
    [columnsWidth setObject:i2n(63) forKey:@"2"];
    [columnsWidth setObject:i2n(50) forKey:@"3"];
    [columnsWidth setObject:i2n(50) forKey:@"4"];
    [columnsWidth setObject:i2n(57) forKey:@"16"];
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
    [_py enable:[ud objectForKey:@"scanTagTrack"] scanForTag:@"track"];
    [_py enable:[ud objectForKey:@"scanTagArtist"] scanForTag:@"artist"];
    [_py enable:[ud objectForKey:@"scanTagAlbum"] scanForTag:@"album"];
    [_py enable:[ud objectForKey:@"scanTagTitle"] scanForTag:@"title"];
    [_py enable:[ud objectForKey:@"scanTagGenre"] scanForTag:@"genre"];
    [_py enable:[ud objectForKey:@"scanTagYear"] scanForTag:@"year"];
    [_py setMinMatchPercentage:[ud objectForKey:@"minMatchPercentage"]];
    [_py setWordWeighting:[ud objectForKey:@"wordWeighting"]];
    [_py setMixFileKind:[ud objectForKey:@"mixFileKind"]];
    [_py setMatchSimilarWords:[ud objectForKey:@"matchSimilarWords"]];
    int r = n2i([py doScan]);
    [matches reloadData];
    [self refreshStats];
    if (r == 1)
        [Dialogs showMessage:@"You cannot make a duplicate scan with only reference directories."];
    if (r == 3)
    {
        [Dialogs showMessage:@"The selected directories contain no scannable file."];
        [app toggleDirectories:nil];
    }
}

- (IBAction)switchSelected:(id)sender
{
    [self performPySelection:[self getSelectedPaths:YES]];
    [py makeSelectedReference];
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
    if (!_detailsPanel)
        _detailsPanel = [[DetailsPanel alloc] initWithPy:py];
    if ([[_detailsPanel window] isVisible])
        [[_detailsPanel window] close];
    else
        [[_detailsPanel window] orderFront:nil];
}

- (IBAction)togglePowerMarker:(id)sender
{
    if ([pmSwitch selectedSegment] == 1)
        [pmSwitch setSelectedSegment:0];
    else
        [pmSwitch setSelectedSegment:1];
    [self changePowerMarker:sender];
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

- (void)performPySelection:(NSArray *)aIndexPaths
{
    if (_powerMode)
        [py selectPowerMarkerNodePaths:aIndexPaths];
    else
        [py selectResultNodePaths:aIndexPaths];
}

- (void)initResultColumns
{
    NSTableColumn *refCol = [matches tableColumnWithIdentifier:@"0"];
    _resultColumns = [[NSMutableArray alloc] init];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"0"]]; // File Name
    [_resultColumns addObject:[self getColumnForIdentifier:1 title:@"Directory" width:120 refCol:refCol]];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"2"]]; // Size
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"3"]]; // Time
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"4"]]; // Bitrate
    [_resultColumns addObject:[self getColumnForIdentifier:5 title:@"Sample Rate" width:60 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:6 title:@"Kind" width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:7 title:@"Creation" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:8 title:@"Modification" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:9 title:@"Title" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:10 title:@"Artist" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:11 title:@"Album" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:12 title:@"Genre" width:80 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:13 title:@"Year" width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:14 title:@"Track Number" width:40 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:15 title:@"Comment" width:120 refCol:refCol]];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"16"]]; // Match %
    [_resultColumns addObject:[self getColumnForIdentifier:17 title:@"Words Used" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:18 title:@"Dupe Count" width:80 refCol:refCol]];
}

-(void)refreshStats
{
    [stats setStringValue:[py getStatLine]];
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
- (void)duplicateSelectionChanged:(NSNotification *)aNotification
{
    if (_detailsPanel)
        [_detailsPanel refresh];
}

- (void)jobCompleted:(NSNotification *)aNotification
{
    [super jobCompleted:aNotification];
    id lastAction = [[ProgressController mainProgressController] jobId];
    if ([lastAction isEqualTo:jobScanDeadTracks])
    {
        int deadTrackCount = [(PyDupeGuru *)py deadTrackCount];
        if (deadTrackCount > 0)
        {
            NSString *msg = @"Your iTunes Library contains %d dead tracks ready to be removed. Continue?";
            if ([Dialogs askYesNo:[NSString stringWithFormat:msg,deadTrackCount]] == NSAlertFirstButtonReturn)
                [(PyDupeGuru *)py removeDeadTracks];
        }
        else
        {
            [Dialogs showMessage:@"You have no dead tracks in your iTunes Library"];
        }
    }
}

- (void)outlineViewSelectionDidChange:(NSNotification *)notification
{
    [self performPySelection:[self getSelectedPaths:NO]];
    [py refreshDetailsWithSelected];
    [[NSNotificationCenter defaultCenter] postNotificationName:DuplicateSelectionChangedNotification object:self];
}

- (void)resultsChanged:(NSNotification *)aNotification
{
    [matches reloadData];
    [self expandAll:nil];
    [self outlineViewSelectionDidChange:nil];
    [self refreshStats];
}

- (void)resultsMarkingChanged:(NSNotification *)aNotification
{
    [matches invalidateMarkings];
    [self refreshStats];
}
@end
