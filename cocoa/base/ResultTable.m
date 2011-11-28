/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ResultTable.h"
#import "Dialogs.h"
#import "Utils.h"
#import "Consts.h"
#import "HSQuicklook.h"

@interface HSTable (private)
- (void)setPySelection;
- (void)setViewSelection;
@end

@implementation ResultTable
- (id)initWithPy:(id)aPy view:(NSTableView *)aTableView
{
    self = [super initWithPy:aPy view:aTableView];
    _deltaColumns = [[NSSet setWithArray:[[self py] deltaColumns]] retain];
    [self connect];
    return self;
}

- (void)dealloc
{
    [self disconnect];
    [_deltaColumns release];
    [super dealloc];
}

- (PyResultTable *)py
{
    return (PyResultTable *)py;
}

/* Private */
- (void)updateQuicklookIfNeeded
{
    if ([[QLPreviewPanel sharedPreviewPanel] dataSource] == self) { 
        [[QLPreviewPanel sharedPreviewPanel] reloadData];
    }
}

- (void)setPySelection
{
    [super setPySelection];
    [self updateQuicklookIfNeeded];
}

- (void)setViewSelection
{
    [super setViewSelection];
    [self updateQuicklookIfNeeded];
}

/* Public */
- (BOOL)powerMarkerMode
{
    return [[self py] powerMarkerMode];
}

- (void)setPowerMarkerMode:(BOOL)aPowerMarkerMode
{
    [[self py] setPowerMarkerMode:aPowerMarkerMode];
}

- (BOOL)deltaValuesMode
{
    return [[self py] deltaValuesMode];
}

- (void)setDeltaValuesMode:(BOOL)aDeltaValuesMode
{
    [[self py] setDeltaValuesMode:aDeltaValuesMode];
}

- (NSInteger)selectedDupeCount
{
    return [[self py] selectedDupeCount];
}

- (void)removeSelected
{
    NSInteger selectedDupeCount = [self selectedDupeCount];
    if (!selectedDupeCount)
        return;
    NSString *msgFmt = TR(@"You are about to remove %d files from results. Continue?");
    NSString *msg = [NSString stringWithFormat:msgFmt,selectedDupeCount];
    if ([Dialogs askYesNo:msg] == NSAlertSecondButtonReturn) // NO
        return;
    [[self py] removeSelected];
}

/* Datasource */
- (id)tableView:(NSTableView *)aTableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    NSString *identifier = [column identifier];
    if ([identifier isEqual:@"marked"]) {
        return [[self py] valueForColumn:@"marked" row:row];
    }
    return [[self py] valueForRow:row column:identifier];
}

- (void)tableView:(NSTableView *)aTableView setObjectValue:(id)object forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    NSString *identifier = [column identifier];
    if ([identifier isEqual:@"marked"]) {
        [[self py] setValue:object forColumn:identifier row:row];
    }
    else if ([identifier isEqual:@"name"]) {
        NSString *oldName = [[self py] valueForRow:row column:identifier];
        NSString *newName = object;
        if (![newName isEqual:oldName]) {
            BOOL renamed = [[self py] renameSelected:newName];
            if (!renamed) {
                [Dialogs showMessage:[NSString stringWithFormat:TR(@"The name '%@' already exists."), newName]];
            }
            else {
                [tableView setNeedsDisplay:YES];
            }
        }
    }
}

/* Delegate */
- (void)tableView:(NSTableView *)aTableView didClickTableColumn:(NSTableColumn *)tableColumn
{
    if ([[tableView sortDescriptors] count] < 1)
        return;
    NSSortDescriptor *sd = [[tableView sortDescriptors] objectAtIndex:0];
    [[self py] sortBy:[sd key] ascending:[sd ascending]];
}

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    BOOL isSelected = [tableView isRowSelected:row];
    BOOL isMarkable = n2b([[self py] valueForColumn:@"markable" row:row]);
    if ([[column identifier] isEqual:@"marked"]) {
        [cell setEnabled:isMarkable];
        // Low-tech solution, for indentation, but it works...
        NSCellImagePosition pos = isMarkable ? NSImageRight : NSImageLeft;
        [cell setImagePosition:pos];
    }
    if ([cell isKindOfClass:[NSTextFieldCell class]]) {
        NSColor *color = [NSColor textColor];
        if (isSelected) {
            color = [NSColor selectedTextColor];
        }
        else if (isMarkable) {
            if ([self deltaValuesMode]) {
                if ([_deltaColumns containsObject:[column identifier]]) {
                    color = [NSColor orangeColor];
                }
            }
        }
        else {
            color = [NSColor blueColor];
        }
        [(NSTextFieldCell *)cell setTextColor:color];
    }
}

- (BOOL)tableViewHadDeletePressed:(NSTableView *)tableView
{
    [self removeSelected];
    return YES;
}

- (BOOL)tableViewHadSpacePressed:(NSTableView *)tableView
{
    [[self py] markSelected];
    return YES;
}

/* Quicklook */
- (NSInteger)numberOfPreviewItemsInPreviewPanel:(QLPreviewPanel *)panel
{
    return [[[self py] selectedRows] count];
}

- (id <QLPreviewItem>)previewPanel:(QLPreviewPanel *)panel previewItemAtIndex:(NSInteger)index
{
    NSArray *selectedRows = [[self py] selectedRows];
    NSInteger absIndex = n2i([selectedRows objectAtIndex:index]);
    NSString *path = [[self py] pathAtIndex:absIndex];
    return [[HSQLPreviewItem alloc] initWithUrl:[NSURL fileURLWithPath:path] title:path];
}

- (BOOL)previewPanel:(QLPreviewPanel *)panel handleEvent:(NSEvent *)event
{
    // redirect all key down events to the table view
    if ([event type] == NSKeyDown) {
        [[self view] keyDown:event];
        return YES;
    }
    return NO;
}

/* Python --> Cocoa */
- (void)invalidateMarkings
{
    [tableView setNeedsDisplay:YES];
}
@end