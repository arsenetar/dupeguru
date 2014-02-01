/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController.h"
#import "PySelectableList.h"

@interface HSSelectableList : HSGUIController <NSTableViewDelegate, NSTableViewDataSource>
{
    NSArray *items;
}
- (id)initWithPyRef:(PyObject *)aPyRef wrapperClass:(Class)aWrapperClass callbackClassName:(NSString *)aCallbackClassName view:(NSTableView *)aTableView;
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(NSTableView *)aTableView;
- (NSTableView *)view;
- (void)setView:(NSTableView *)aTableView;
- (PySelectableList *)model;

- (void)refresh;
@end
