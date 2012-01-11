/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Python.h>
#import "StatsLabel.h"
#import "ObjP.h"

@implementation StatsLabel
- (id)initWithLabelView:(NSTextField *)aLabelView
{
    self = [self init];
    view = [aLabelView retain];
    PyGILState_STATE gilState = PyGILState_Ensure();
    PyObject *pModule = PyImport_AddModule("__main__");
    PyObject *pAppInstance = PyObject_GetAttrString(pModule, "APP_INSTANCE");
    PyObject *pStatsLabel = PyObject_GetAttrString(pAppInstance, "stats_label");
    PyObject *pCallback = ObjP_classInstanceWithRef(@"StatsLabelView", @"inter.StatsLabelView", self);
    py = [[PyStatsLabel alloc] initWithModel:pStatsLabel Callback:pCallback];
    PyGILState_Release(gilState);
    [[self py] connect];
    return self;
}

- (void)dealloc
{
    [[self py] disconnect];
    [py release];
    [view release];
    [super dealloc];
}

- (PyStatsLabel *)py
{
    return (PyStatsLabel *)py;
}

- (NSTextField *)labelView
{
    return (NSTextField *)view;
}

/* Python --> Cocoa */
- (void)refresh
{
    [[self labelView] setStringValue:[[self py] display]];
}
@end
