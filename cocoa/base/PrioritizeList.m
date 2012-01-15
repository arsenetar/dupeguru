/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "PrioritizeList.h"
#import "Utils.h"
#import "Consts.h"

@implementation PrioritizeList
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(NSTableView *)aTableView
{
    self = [super initWithPyRef:aPyRef wrapperClass:[PyPrioritizeList class]
        callbackClassName:@"PrioritizeListView" view:aTableView];
    return self;
}

- (PyPrioritizeList *)model
{
    return (PyPrioritizeList *)model;
}

- (void)setView:(NSTableView *)aTableView
{
    [super setView:aTableView];
    [[self view] registerForDraggedTypes:[NSArray arrayWithObject:DGPrioritizeIndexPasteboardType]];
}

- (BOOL)tableView:(NSTableView *)tv writeRowsWithIndexes:(NSIndexSet *)rowIndexes toPasteboard:(NSPasteboard*)pboard
{
    NSData *data = [NSKeyedArchiver archivedDataWithRootObject:rowIndexes];
    [pboard declareTypes:[NSArray arrayWithObject:DGPrioritizeIndexPasteboardType] owner:self];
    [pboard setData:data forType:DGPrioritizeIndexPasteboardType];
    return YES;
}

- (NSDragOperation)tableView:(NSTableView*)tv validateDrop:(id <NSDraggingInfo>)info proposedRow:(NSInteger)row 
       proposedDropOperation:(NSTableViewDropOperation)op
{
    if (op == NSTableViewDropAbove) {
        return NSDragOperationMove;
    }
    return NSDragOperationNone;
}

- (BOOL)tableView:(NSTableView *)aTableView acceptDrop:(id <NSDraggingInfo>)info
              row:(NSInteger)row dropOperation:(NSTableViewDropOperation)operation
{
    NSPasteboard* pboard = [info draggingPasteboard];
    NSData* rowData = [pboard dataForType:DGPrioritizeIndexPasteboardType];
    NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
    [[self model] moveIndexes:[Utils indexSet2Array:rowIndexes] toIndex:row];
    return YES;
}
@end