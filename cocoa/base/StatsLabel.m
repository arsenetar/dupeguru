/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "StatsLabel.h"
#import "Utils.h"

@implementation StatsLabel
- (id)initWithPyRef:(PyObject *)aPyRef view:(NSTextField *)aLabelView
{
    return [super initWithPyRef:aPyRef wrapperClass:[PyStatsLabel class]
        callbackClassName:@"StatsLabelView" view:aLabelView];
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
