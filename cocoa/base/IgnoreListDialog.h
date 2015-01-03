/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyIgnoreListDialog.h"
#import "HSTable.h"

@interface IgnoreListDialog : NSWindowController
{
    PyIgnoreListDialog *model;
    HSTable *ignoreListTable;
    NSTableView *ignoreListTableView;
}

@property (readwrite, retain) PyIgnoreListDialog *model;
@property (readwrite, retain) NSTableView *ignoreListTableView;

- (id)initWithPyRef:(PyObject *)aPyRef;
- (void)initializeColumns;
@end