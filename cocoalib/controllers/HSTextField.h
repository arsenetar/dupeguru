/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import <Python.h>
#import "HSGUIController.h"
#import "PyTextField.h"

@interface HSTextField : HSGUIController <NSTextFieldDelegate> {}
- (id)initWithPyRef:(PyObject *)aPyRef view:(NSTextField *)aView;
- (NSTextField *)view;
- (void)setView:(NSTextField *)aView;
- (PyTextField *)model;

- (void)refresh;
@end