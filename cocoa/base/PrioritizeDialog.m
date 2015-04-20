/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "PrioritizeDialog.h"
#import "PrioritizeDialog_UI.h"
#import "HSPyUtil.h"

@implementation PrioritizeDialog

@synthesize categoryPopUpView;
@synthesize criteriaTableView;
@synthesize prioritizationTableView;

- (id)initWithApp:(PyDupeGuru *)aApp
{
    self = [super initWithWindowNibName:@"PrioritizeDialog"];
    model = [[PyPrioritizeDialog alloc] initWithApp:[aApp pyRef]];
    [self setWindow:createPrioritizeDialog_UI(self)];
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

- (void)ok
{
    [NSApp stopModal];
    [self close];
}

- (void)cancel
{
    [NSApp abortModal];
    [self close];
}
@end