/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "IgnoreListDialog.h"
#import "IgnoreListDialog_UI.h"
#import "HSPyUtil.h"

@implementation IgnoreListDialog

@synthesize model;
@synthesize ignoreListTableView;

- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithWindow:nil];
    self.model = [[[PyIgnoreListDialog alloc] initWithModel:aPyRef] autorelease];
    [self.model bindCallback:createCallback(@"IgnoreListDialogView", self)];
    [self setWindow:createIgnoreListDialog_UI(self)];
    ignoreListTable = [[HSTable alloc] initWithPyRef:[model ignoreListTable] tableView:ignoreListTableView];
    [self initializeColumns];
    return self;
}

- (void)dealloc
{
    [ignoreListTable release];
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

/* model --> view */
- (void)show
{
    [self showWindow:self];
}
@end