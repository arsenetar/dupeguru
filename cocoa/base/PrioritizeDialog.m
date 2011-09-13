/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "PrioritizeDialog.h"

@implementation PrioritizeDialog
- (id)initWithPy:(PyApp *)aPy
{
    self = [super initWithNibName:@"PrioritizeDialog" pyClassName:@"PyPrioritizeDialog" pyParent:aPy];
    [self window];
    categoryPopUp = [[HSPopUpList alloc] initWithPy:[[self py] categoryList] view:categoryPopUpView];
    criteriaList = [[HSSelectableList alloc] initWithPy:[[self py] criteriaList] view:criteriaTableView];
    prioritizationList = [[HSSelectableList alloc] initWithPy:[[self py] prioritizationList] view:prioritizationTableView];
    [self connect];
    return self;
}

- (void)dealloc
{
    [self disconnect];
    [categoryPopUp release];
    [criteriaList release];
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
}

- (IBAction)cancel:(id)sender
{
    [NSApp abortModal];
}
@end