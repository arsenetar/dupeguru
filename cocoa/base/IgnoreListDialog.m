/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "IgnoreListDialog.h"
#import "Utils.h"

@implementation IgnoreListDialog
- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithWindowNibName:@"IgnoreListDialog"];
    [self window]; //So the detailsTable is initialized.
    model = [[PyIgnoreListDialog alloc] initWithModel:aPyRef];
    [model bindCallback:createCallback(@"IgnoreListDialogView", self)];
    ignoreListTable = [[HSTable alloc] initWithPyRef:[model ignoreListTable] tableView:ignoreListTableView];
    [self initializeColumns];
    return self;
}

- (void)dealloc
{
    [ignoreListTable release];
    [model release];
    [super dealloc];
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"path1", 240, 40, 0, NO, nil},
        {@"path2", 240, 40, 0, NO, nil},
        nil
    };
    [[ignoreListTable columns] initializeColumns:defs];
    [[ignoreListTable columns] setColumnsAsReadOnly];
}

- (IBAction)removeSelected:(id)sender
{
    [model removeSelected];
}

- (IBAction)clear:(id)sender
{
    [model clear];
}

/* model --> view */
- (void)show
{
    [self showWindow:self];
}
@end