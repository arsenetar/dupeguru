/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import <Python.h>
#import "HSGUIController.h"
#import "PyColumns.h"

/*
    This structure is to define constants describing table columns (it's easier to maintain in code
    than in XIB files).
*/
typedef struct {
    NSString *attrname;
    NSUInteger defaultWidth;
    NSUInteger minWidth;
    NSUInteger maxWidth;
    BOOL sortable;
    Class cellClass;
} HSColumnDef;

@interface HSColumns : HSGUIController {}
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(NSTableView *)aTableView;
- (PyColumns *)model;
- (NSTableView *)view;
- (void)connectNotifications;
- (void)disconnectNotifications;
- (void)initializeColumns:(HSColumnDef *)columns;
- (void)initializeColumnsFromModel:(HSColumnDef)columnModel;
- (void)setColumnsAsReadOnly;
- (void)restoreColumns;
- (void)setColumn:(NSString *)colname visible:(BOOL)visible;
@end