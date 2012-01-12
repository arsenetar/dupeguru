/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "StatsLabel.h"
#import "Utils.h"

@implementation StatsLabel
- (id)initWithLabelView:(NSTextField *)aLabelView
{
    self = [self init];
    view = [aLabelView retain];
    py = createPyWrapper(@"PyStatsLabel", @"stats_label", @"StatsLabelView", self);
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
