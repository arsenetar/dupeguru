/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ProblemDialog.h"
#import "Utils.h"

@implementation ProblemDialog
- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithWindowNibName:@"ProblemDialog"];
    [self window]; //So the detailsTable is initialized.
    model = [[PyProblemDialog alloc] initWithModel:aPyRef];
    problemTable = [[HSTable alloc] initWithPyRef:[model problemTable] tableView:problemTableView];
    [self initializeColumns];
    return self;
}

- (void)dealloc
{
    [problemTable release];
    [model release];
    [super dealloc];
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"path", 202, 40, 0, NO, nil},
        {@"msg", 228, 40, 0, NO, nil},
        nil
    };
    [[problemTable columns] initializeColumns:defs];
}

- (IBAction)revealSelected:(id)sender
{
    [model revealSelected];
}
@end