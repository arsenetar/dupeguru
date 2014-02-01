/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController.h"
#import "HSTextField.h"
#import "Worker.h"
#import "PyProgressWindow.h"

@interface HSProgressWindow : HSGUIController <Worker>
{
    NSInteger progress;
    HSTextField *jobdescTextField;
    HSTextField *progressdescTextField;
    NSWindow *parentWindow;
}

- (id)initWithPyRef:(PyObject *)aPyRef view:(NSView *)aView;
- (PyProgressWindow *)model;
- (void)setParentWindow:(NSWindow *)aParentWindow;

- (void)setProgress:(NSInteger)aProgress;
- (void)showWindow;
- (void)closeWindow;
@end