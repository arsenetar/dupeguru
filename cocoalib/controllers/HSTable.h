/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController.h"
#import "HSColumns.h"
#import "PyTable.h"

@interface HSTable : HSGUIController <NSTableViewDelegate, NSTableViewDataSource>
{
    HSColumns *columns;
}
- (id)initWithModel:(PyTable *)aModel tableView:(NSTableView *)aTableView;
- (id)initWithPyRef:(PyObject *)aPyRef wrapperClass:(Class)aWrapperClass callbackClassName:(NSString *)aCallbackClassName view:(NSTableView *)aTableView;
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(NSTableView *)aTableView;

/* Virtual */
- (PyTable *)model;
- (NSTableView *)view;
- (void)setView:(NSTableView *)aTableView;

/* Public */
- (HSColumns *)columns;
- (void)refresh;
- (void)showSelectedRow;
- (void)updateSelection;
@end
