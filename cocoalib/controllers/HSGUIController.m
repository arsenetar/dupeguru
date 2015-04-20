/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSGUIController.h"
#import "HSPyUtil.h"

@implementation HSGUIController
- (id)initWithModel:(PyGUIObject *)aModel
{
    self = [super init];
    model = [aModel retain];
    view = nil;
    return self;
}

- (id)initWithModel:(PyGUIObject *)aModel view:(NSView *)aView
{
    self = [super init];
    model = [aModel retain];
    [self setView:aView];
    return self;
}

- (id)initWithPyRef:(PyObject *)aPyRef wrapperClass:(Class)aWrapperClass callbackClassName:(NSString *)aCallbackClassName view:(NSView *)aView
{
    PyGUIObject *m = [[aWrapperClass alloc] initWithModel:aPyRef];
    self = [self initWithModel:m view:aView];
    [m bindCallback:createCallback(aCallbackClassName, self)];
    [m release];
    return self;
}

- (void)dealloc
{
    // NSLog([NSString stringWithFormat:@"%@ dealloc",[[self class] description]]);
    [self setView:nil];
    [model free];
    [model release];
    [super dealloc];
}

- (PyGUIObject *)model
{
    return model;
}

- (NSView *)view
{
    return view;
}

- (void)setView:(NSView *)aView
{
    [view release];
    view = [aView retain];
}
@end
