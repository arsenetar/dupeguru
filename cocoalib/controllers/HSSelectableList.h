/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
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
