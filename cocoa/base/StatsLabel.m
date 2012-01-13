/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "StatsLabel.h"
#import "Utils.h"

@implementation StatsLabel
- (id)initWithPyRef:(PyObject *)aPyRef view:(NSTextField *)aLabelView
{
    PyStatsLabel *m = [[PyStatsLabel alloc] initWithModel:aPyRef];
    self = [self initWithModel:m view:aLabelView];
    [m bindCallback:createCallback(@"StatsLabelView", self)];
    [m connect];
    [m release];
    return self;
}

- (void)dealloc
{
    [[self model] disconnect];
    [model release];
    [view release];
    [super dealloc];
}

- (PyStatsLabel *)model
{
    return (PyStatsLabel *)model;
}

- (NSTextField *)labelView
{
    return (NSTextField *)view;
}

/* Python --> Cocoa */
- (void)refresh
{
    [[self labelView] setStringValue:[[self model] display]];
}
@end
