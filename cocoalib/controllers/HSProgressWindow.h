/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
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