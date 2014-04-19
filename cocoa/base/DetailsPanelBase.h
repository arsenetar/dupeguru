/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import <Python.h>
#import "PyDetailsPanel.h"

@interface DetailsPanelBase : NSWindowController <NSTableViewDataSource>
{
    NSTableView *detailsTable;
    
    PyDetailsPanel *model;
}

@property (readwrite, retain) NSTableView *detailsTable;

- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyDetailsPanel *)model;

- (NSWindow *)createWindow;
- (BOOL)isVisible;
- (void)toggleVisibility;

/* Python --> Cocoa */
- (void)refresh;
@end