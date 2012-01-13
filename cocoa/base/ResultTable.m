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
- (id)initWithPyRef:(PyObject *)aPyRef view:(NSTableView *)aTableView
{
    PyResultTable *m = [[PyResultTable alloc] initWithModel:aPyRef];
    self = [super initWithModel:m tableView:aTableView];
    [m bindCallback:createCallback(@"ResultTableView", self)];
    [m release];
    _deltaColumns = [[NSSet setWithArray:[[self model] deltaColumns]] retain];
    [model connect];
    return self;
}

- (void)dealloc
{
    [model disconnect];
    [_deltaColumns release];
    [super dealloc];
}

- (PyResultTable *)model
{
    return (PyResultTable *)model;
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
    return [[self model] powerMarkerMode];
}

- (void)setPowerMarkerMode:(BOOL)aPowerMarkerMode
{
    [[self model] setPowerMarkerMode:aPowerMarkerMode];
}

- (BOOL)deltaValuesMode
{
    return [[self model] deltaValuesMode];
}

- (void)setDeltaValuesMode:(BOOL)aDeltaValuesMode
{
    [[self model] setDeltaValuesMode:aDeltaValuesMode];
}

- (NSInteger)selectedDupeCount
{
    return [[self model] selectedDupeCount];
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
    [[self model] removeSelected];
}

/* Datasource */
- (id)tableView:(NSTableView *)aTableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    NSString *identifier = [column identifier];
    if ([identifier isEqual:@"marked"]) {
        return [[self model] valueForColumn:@"marked" row:row];
    }
    return [[self model] valueForRow:row column:identifier];
}

- (void)tableView:(NSTableView *)aTableView setObjectValue:(id)object forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    NSString *identifier = [column identifier];
    if ([identifier isEqual:@"marked"]) {
        [[self model] setValue:object forColumn:identifier row:row];
    }
    else if ([identifier isEqual:@"name"]) {
        NSString *oldName = [[self model] valueForRow:row column:identifier];
        NSString *newName = object;
        if (![newName isEqual:oldName]) {
            BOOL renamed = [[self model] renameSelected:newName];
            if (!renamed) {
                [Dialogs showMessage:[NSString stringWithFormat:TR(@"The name '%@' already exists."), newName]];
            }
            else {
                [[self view] setNeedsDisplay:YES];
            }
        }
    }
}

/* Delegate */
- (void)tableView:(NSTableView *)aTableView didClickTableColumn:(NSTableColumn *)tableColumn
{
    if ([[[self view] sortDescriptors] count] < 1)
        return;
    NSSortDescriptor *sd = [[[self view] sortDescriptors] objectAtIndex:0];
    [[self model] sortBy:[sd key] ascending:[sd ascending]];
}

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    BOOL isSelected = [[self view] isRowSelected:row];
    BOOL isMarkable = n2b([[self model] valueForColumn:@"markable" row:row]);
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
    [[self model] markSelected];
    return YES;
}

/* Quicklook */
- (NSInteger)numberOfPreviewItemsInPreviewPanel:(QLPreviewPanel *)panel
{
    return [[[self model] selectedRows] count];
}

- (id <QLPreviewItem>)previewPanel:(QLPreviewPanel *)panel previewItemAtIndex:(NSInteger)index
{
    NSArray *selectedRows = [[self model] selectedRows];
    NSInteger absIndex = n2i([selectedRows objectAtIndex:index]);
    NSString *path = [[self model] pathAtIndex:absIndex];
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
    [[self view] setNeedsDisplay:YES];
}
@end