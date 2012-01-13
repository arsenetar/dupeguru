/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "PrioritizeDialog.h"
#import "Utils.h"

@implementation PrioritizeDialog
- (id)init
{
    self = [super initWithWindowNibName:@"PrioritizeDialog"];
    [self window];
    py = [[PyPrioritizeDialog alloc] initWithModel:findHackishModel(@"prioritize_dialog")];
    [py bindCallback:createCallback(@"PrioritizeDialogView", self)];
    categoryPopUp = [[HSPopUpList alloc] initWithPyRef:[[self py] categoryList] popupView:categoryPopUpView];
    criteriaList = [[HSSelectableList alloc] initWithPyRef:[[self py] criteriaList] tableView:criteriaTableView];
    prioritizationList = [[PrioritizeList alloc] initWithPyRef:[[self py] prioritizationList] tableView:prioritizationTableView];
    [py connect];
    return self;
}

- (void)dealloc
{
    [py disconnect];
    [categoryPopUp release];
    [criteriaList release];
    [prioritizationList release];
    [super dealloc];
}

- (PyPrioritizeDialog *)py
{
    return (PyPrioritizeDialog *)py;
}

- (IBAction)addSelected:(id)sender
{
    [[self py] addSelected];
}

- (IBAction)removeSelected:(id)sender
{
    [[self py] removeSelected];
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