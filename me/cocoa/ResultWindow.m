/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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
    [[self window] setTitle:@"dupeGuru Music Edition"];
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
    [self refreshStats];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(resultsMarkingChanged:) name:ResultsMarkingChangedNotification object:nil];
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
- (void)initResultColumns
{
    NSTableColumn *refCol = [matches tableColumnWithIdentifier:@"0"];
    _resultColumns = [[NSMutableArray alloc] init];
    [_resultColumns addObject:[matches tableColumnWithIdentifier:@"0"]]; // File Name
    [_resultColumns addObject:[self getColumnForIdentifier:1 title:@"Directory" width:120 refCol:refCol]];
    NSTableColumn *sizeCol = [self getColumnForIdentifier:2 title:@"Size (MB)" width:63 refCol:refCol];
    [[sizeCol dataCell] setAlignment:NSRightTextAlignment];
    [_resultColumns addObject:sizeCol];
    NSTableColumn *timeCol = [self getColumnForIdentifier:3 title:@"Time" width:50 refCol:refCol];
    [[timeCol dataCell] setAlignment:NSRightTextAlignment];
    [_resultColumns addObject:timeCol];
    NSTableColumn *brCol = [self getColumnForIdentifier:4 title:@"Bitrate" width:50 refCol:refCol];
    [[brCol dataCell] setAlignment:NSRightTextAlignment];
    [_resultColumns addObject:brCol];
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
    [_resultColumns addObject:[self getColumnForIdentifier:16 title:@"Match %" width:57 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:17 title:@"Words Used" width:120 refCol:refCol]];
    [_resultColumns addObject:[self getColumnForIdentifier:18 title:@"Dupe Count" width:80 refCol:refCol]];
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

- (void)resultsMarkingChanged:(NSNotification *)aNotification
{
    [matches invalidateMarkings];
    [self refreshStats];
}
@end
