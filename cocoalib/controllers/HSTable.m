/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSTable.h"
#import "Utils.h"

@implementation HSTable
- (id)initWithModel:(PyTable *)aModel tableView:(NSTableView *)aTableView
{
    self = [super initWithModel:aModel view:aTableView];
    columns = [[HSColumns alloc] initWithPyRef:[[self model] columns] tableView:aTableView];
    return self;
}

- (id)initWithPyRef:(PyObject *)aPyRef wrapperClass:(Class)aWrapperClass callbackClassName:(NSString *)aCallbackClassName view:(NSTableView *)aTableView
{
    self = [super initWithPyRef:aPyRef wrapperClass:aWrapperClass callbackClassName:aCallbackClassName view:aTableView];
    columns = [[HSColumns alloc] initWithPyRef:[[self model] columns] tableView:aTableView];
    return self;
}

- (id)initWithPyRef:(PyObject *)aPyRef tableView:(NSTableView *)aTableView
{
    return [self initWithPyRef:aPyRef wrapperClass:[PyTable class] callbackClassName:@"TableView" view:aTableView];
}

- (void)dealloc
{
    [columns release];
    [super dealloc];
}

/* Private */
- (void)setPySelection
{
    NSArray *selection = [Utils indexSet2Array:[[self view] selectedRowIndexes]];
    NSArray *pyselection = [[self model] selectedRows];
    if (![selection isEqualTo:pyselection])
        [[self model] selectRows:selection];
}

- (void)setViewSelection
{
    NSIndexSet *selection = [Utils array2IndexSet:[[self model] selectedRows]];
	[[self view] selectRowIndexes:selection byExtendingSelection:NO];
}

/* HSGUIController */
- (PyTable *)model
{
    return (PyTable *)model;
}

- (NSTableView *)view
{
    return (NSTableView *)view;
}

- (void)setView:(NSTableView *)aTableView
{
    if ([self view] != nil) {
        [[self view] setDataSource:nil];
        [[self view] setDelegate:nil];
    }
    [super setView:aTableView];
    if (aTableView != nil) {
        [aTableView setDataSource:self];
        [aTableView setDelegate:self];
    }
}

/* Data source */
- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView
{
    return [[self model] numberOfRows];
}

- (id)tableView:(NSTableView *)tableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self model] numberOfRows]) {
        return @"";
    }
    return [[self model] valueForColumn:[column identifier] row:row];
}

/* NSTableView Delegate */
- (void)tableView:(NSTableView *)aTableView didClickTableColumn:(NSTableColumn *)column
{
    if ([[aTableView sortDescriptors] count] == 0) {
        return;
    }
    NSSortDescriptor *sd = [[aTableView sortDescriptors] objectAtIndex:0];
    [[self model] sortByColumn:[sd key] desc:![sd ascending]];
}

// See HSOutline.outlineViewSelectionIsChanging: to know why we update selection in both notifs
- (void)tableViewSelectionIsChanging:(NSNotification *)notification
{
    [self setPySelection];
}

- (void)tableViewSelectionDidChange:(NSNotification *)notification
{
    [self setPySelection];
}

/* Public */
- (HSColumns *)columns
{
    return columns;
}

- (void)refresh
{
    // If we just deleted the last item, we want to update the selection before we reload
    [self setViewSelection];
    [[self view] reloadData];
    [self setViewSelection];
}

- (void)showSelectedRow
{
    [[self view] scrollRowToVisible:[[self view] selectedRow]];
}

- (void)updateSelection
{
    [self setViewSelection];
}
@end
