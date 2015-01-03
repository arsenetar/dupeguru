/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSPopUpList.h"
#import "Utils.h"

@implementation HSPopUpList
- (id)initWithPyRef:(PyObject *)aPyRef popupView:(NSPopUpButton *)aPopupView
{
    self = [super initWithPyRef:aPyRef wrapperClass:[PySelectableList class]
        callbackClassName:@"SelectableListView" view:aPopupView];
    return self;
}

- (NSPopUpButton *)view
{
    return (NSPopUpButton *)view;
}

- (void)setView:(NSPopUpButton *)aPopupView
{
    if ([self view] != nil) {
        [[self view] setTarget:nil];
    }
    [super setView:aPopupView];
    if (aPopupView != nil) {
        [aPopupView setAction:@selector(popupViewSelectionChanged)];
        [aPopupView setTarget:self];
        [self refresh];
    }
}

- (PySelectableList *)model
{
    return (PySelectableList *)model;
}

- (void)popupViewSelectionChanged
{
    [[self model] selectIndex:[[self view] indexOfSelectedItem]];
}

/* model --> view */
- (void)refresh
{
    [[self view] removeAllItems];
    [[self view] addItemsWithTitles:[[self model] items]];
    [self updateSelection];
}

- (void)updateSelection
{
    [[self view] selectItemAtIndex:[[self model] selectedIndex]]; 
}
@end