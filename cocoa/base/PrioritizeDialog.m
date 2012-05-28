/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "PrioritizeDialog.h"
#import "HSPyUtil.h"

@implementation PrioritizeDialog
- (id)initWithApp:(PyDupeGuru *)aApp
{
    self = [super initWithWindowNibName:@"PrioritizeDialog"];
    [self window];
    model = [[PyPrioritizeDialog alloc] initWithApp:[aApp pyRef]];
    categoryPopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] categoryList] popupView:categoryPopUpView];
    criteriaList = [[HSSelectableList alloc] initWithPyRef:[[self model] criteriaList] tableView:criteriaTableView];
    prioritizationList = [[PrioritizeList alloc] initWithPyRef:[[self model] prioritizationList] tableView:prioritizationTableView];
    [model bindCallback:createCallback(@"PrioritizeDialogView", self)];
    return self;
}

- (void)dealloc
{
    [categoryPopUp release];
    [criteriaList release];
    [prioritizationList release];
    [model release];
    [super dealloc];
}

- (PyPrioritizeDialog *)model
{
    return (PyPrioritizeDialog *)model;
}

- (IBAction)addSelected:(id)sender
{
    [[self model] addSelected];
}

- (IBAction)removeSelected:(id)sender
{
    [[self model] removeSelected];
}

- (IBAction)ok:(id)sender
{
    [NSApp stopModal];
    [self close];
}

- (IBAction)cancel:(id)sender
{
    [NSApp abortModal];
    [self close];
}
@end