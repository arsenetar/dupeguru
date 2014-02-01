/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "HSTextField.h"
#import "Utils.h"

@implementation HSTextField
- (id)initWithPyRef:(PyObject *)aPyRef view:(NSTextField *)aView
{
    self = [super initWithPyRef:aPyRef wrapperClass:[PyTextField class]
        callbackClassName:@"GUIObjectView" view:aView];
    return self;
}

- (NSTextField *)view
{
    return (NSTextField *)view;
}

- (void)setView:(NSTextField *)aView
{
    if ([self view] != nil) {
        [[self view] setDelegate:nil];
    }   
    [super setView:aView];
    if (aView != nil) {
        [aView setDelegate:self];
        [self refresh];
    }
}

- (PyTextField *)model
{
    return (PyTextField *)model;
}

/* Delegate */
- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    [[self model] setText:[[self view] stringValue]];
}

/* model --> view */
- (void)refresh
{
    [[self view] setStringValue:[[self model] text]];
}
@end