/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ResultTable.h"
#import "Dialogs.h"
#import "Utils.h"
#import "Consts.h"

@implementation ResultTable
- (id)initWithPyParent:(id)aPyParent view:(NSTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyResultTable" pyParent:aPyParent view:aTableView];
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

- (void)setDeltaColumns:(NSIndexSet *)aDeltaColumns
{
    [_deltaColumns release];
    _deltaColumns = [aDeltaColumns retain];
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
    NSString *msg = [NSString stringWithFormat:@"You are about to remove %d files from results. Continue?",selectedDupeCount];
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
    NSInteger columnId = [identifier integerValue];
    return [[self py] valueForRow:row column:columnId];
}

- (void)tableView:(NSTableView *)aTableView setObjectValue:(id)object forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    NSString *identifier = [column identifier];
    if ([identifier isEqual:@"marked"]) {
        [[self py] setValue:object forColumn:identifier row:row];
    }
    else if ([identifier isEqual:@"0"]) {
        NSString *oldName = [[self py] valueForRow:row column:0];
        NSString *newName = object;
        if (![newName isEqual:oldName]) {
            BOOL renamed = [[self py] renameSelected:newName];
            if (!renamed) {
                [Dialogs showMessage:[NSString stringWithFormat:@"The name '%@' already exists.", newName]];
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
    [[self py] sortBy:[[sd key] integerValue] ascending:[sd ascending]];
}

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{ 
    BOOL isMarkable = n2b([[self py] valueForColumn:@"markable" row:row]);
    if ([[column identifier] isEqual:@"marked"]) {
        [cell setEnabled:isMarkable];
        // Low-tech solution, for indentation, but it works...
        NSCellImagePosition pos = isMarkable ? NSImageRight : NSImageLeft;
        [cell setImagePosition:pos];
    }
    if ([cell isKindOfClass:[NSTextFieldCell class]]) {
        // Determine if the text color will be blue due to directory being reference.
        NSTextFieldCell *textCell = cell;
        if (isMarkable) {
            [textCell setTextColor:[NSColor blackColor]];
        }
        else {
            [textCell setTextColor:[NSColor blueColor]];
            if ([self deltaValuesMode]) {
                NSInteger i = [[column identifier] integerValue];
                if ([_deltaColumns containsIndex:i]) {
                    [textCell setTextColor:[NSColor orangeColor]];
                }
            }
        }
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

/* Python --> Cocoa */
- (void)invalidateMarkings
{
    [tableView setNeedsDisplay:YES];
}
@end