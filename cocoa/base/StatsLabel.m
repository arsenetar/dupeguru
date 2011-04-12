/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "StatsLabel.h"
#import "Utils.h"

@implementation StatsLabel
- (id)initWithPyParent:(id)aPyParent labelView:(NSTextField *)aLabelView
{
    self = [super initWithPyClassName:@"PyStatsLabel" pyParent:aPyParent];
    labelView = [aLabelView retain];
    [self connect];
    return self;
}

- (void)dealloc
{
    [self disconnect];
    [labelView release];
    [super dealloc];
}

- (PyStatsLabel *)py
{
    return (PyStatsLabel *)py;
}

/* Python --> Cocoa */
- (void)refresh
{
    [labelView setStringValue:[[self py] display]];
}
@end
