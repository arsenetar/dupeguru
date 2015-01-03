/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSComboBox.h"
#import "HSPyUtil.h"

@implementation HSComboBox
- (id)initWithPyRef:(PyObject *)aPyRef view:(NSComboBox *)aView
{
    PySelectableList *m = [[PySelectableList alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"SelectableListView", self)];
    [m release];
    [self setView:aView];
    return self;
}

- (void)dealloc
{
    [[self view] setTarget:nil];
    [[self view] setDataSource:nil];
    [items release];
    [super dealloc];
}

- (NSComboBox *)view
{
    return (NSComboBox *)view;
}

- (void)setView:(NSComboBox *)aComboboxView
{
    if ([self view] != nil) {
        [[self view] setDataSource:nil];
        [[self view] setTarget:nil];
    }
    [super setView:aComboboxView];
    if (aComboboxView != nil) {
        [aComboboxView setUsesDataSource:YES];
        [aComboboxView setDataSource:self];
        [aComboboxView setAction:@selector(comboboxViewSelectionChanged)];
        [aComboboxView setTarget:self];
        /* This is required for the combobox to send its action whenever it's changed. Normally, it's
           already set, but then the combobox is created programmatically (xibless), it's not. We
           make sure it is here.
        */
        [[aComboboxView cell] setSendsActionOnEndEditing:YES];
        [self refresh];
    }
}

- (PySelectableList *)model
{
    return (PySelectableList *)model;
}

- (void)comboboxViewSelectionChanged
{
    NSInteger index = [[self view] indexOfSelectedItem];
    if (index >= 0) {
        [[self model] selectIndex:index];
    }
}

/* data source */
- (id)comboBox:(NSComboBox *)aComboBox objectValueForItemAtIndex:(NSInteger)index
{
    if (index < 0) {
        return nil;
    }
    return [items objectAtIndex:index];
}

- (NSInteger)numberOfItemsInComboBox:(NSComboBox *)aComboBox
{
    return [items count];
}

- (NSUInteger)comboBox:(NSComboBox *)aComboBox indexOfItemWithStringValue:(NSString *)aString
{
    NSInteger index = [[self model] searchByPrefix:aString];
    if (index >= 0) {
        return index;
    }
    else {
        return NSNotFound;
    }
}

- (NSString *)comboBox:(NSComboBox *)aComboBox completedString:(NSString *)uncompletedString
{
    NSInteger index = [[self model] searchByPrefix:uncompletedString];
    if (index >= 0) {
        return [items objectAtIndex:index];
    }
    else {
        return nil;
    }
}

/* model --> view */
- (void)refresh
{
    [items release];
    items = [[[self model] items] retain];
    [[self view] reloadData];
    [self updateSelection];
}

- (void)updateSelection
{
    [[self view] selectItemAtIndex:[[self model] selectedIndex]]; 
}
@end