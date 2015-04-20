/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSSelectableList.h"
#import "Utils.h"

@implementation HSSelectableList
- (id)initWithPyRef:(PyObject *)aPyRef wrapperClass:(Class)aWrapperClass callbackClassName:(NSString *)aCallbackClassName view:(NSTableView *)aTableView;
{
    self = [super initWithPyRef:aPyRef wrapperClass:aWrapperClass callbackClassName:aCallbackClassName view:aTableView];
    return self;
}

- (id)initWithPyRef:(PyObject *)aPyRef tableView:(NSTableView *)aTableView
{
    self = [self initWithPyRef:aPyRef wrapperClass:[PySelectableList class] callbackClassName:@"SelectableListView" view:aTableView];
    return self;
}

- (void)dealloc
{
    [items release];
    [super dealloc];
}

- (PySelectableList *)model
{
    return (PySelectableList *)model;
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
        [self refresh];
    }
}

/* Private */
- (void)setPySelection
{
    NSArray *selection = [Utils indexSet2Array:[[self view] selectedRowIndexes]];
    NSArray *pyselection = [[self model] selectedIndexes];
    if (![selection isEqualTo:pyselection]) {
        [[self model] selectIndexes:selection];
    }
}

- (void)setViewSelection
{
    NSIndexSet *selection = [Utils array2IndexSet:[[self model] selectedIndexes]];
    [[self view] selectRowIndexes:selection byExtendingSelection:NO];
}

/* Data source */
- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView
{
    return [items count];
}

- (id)tableView:(NSTableView *)tableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [items count]) {
        return @"";
    }
    return [items objectAtIndex:row];
}

- (void)tableViewSelectionDidChange:(NSNotification *)notification
{
    [self setPySelection];
}

/* Public */

- (void)refresh
{
    // If we just deleted the last item, we want to update the selection before we reload
    [items release];
    items = [[[self model] items] retain];
    [[self view] reloadData];
    [self setViewSelection];
}

- (void)updateSelection
{
    NSIndexSet *selection = [NSIndexSet indexSetWithIndex:[[self model] selectedIndex]];
    [[self view] selectRowIndexes:selection byExtendingSelection:NO];
}
@end
