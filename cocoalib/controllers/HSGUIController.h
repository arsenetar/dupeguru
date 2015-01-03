/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import "PyGUIObject.h"

@interface HSGUIController : NSObject
{
    PyGUIObject *model;
    NSView *view;
}
- (id)initWithModel:(PyGUIObject *)aPy;
- (id)initWithModel:(PyGUIObject *)aPy view:(NSView *)aView;
- (id)initWithPyRef:(PyObject *)aPyRef wrapperClass:(Class)aWrapperClass callbackClassName:(NSString *)aCallbackClassName view:(NSView *)aView;
- (PyGUIObject *)model;
- (NSView *)view;
- (void)setView:(NSView *)aView;
@end
