/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ExtraFairwareReminder.h"
#import "Utils.h"

@implementation ExtraFairwareReminder
- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithWindowNibName:@"ExtraFairwareReminder"];
    [self window];
    [continueButton setEnabled:NO];
    model = [[PyExtraFairwareReminder alloc] initWithModel:aPyRef];
    [model bindCallback:createCallback(@"ExtraFairwareReminderView", self)];
    return self;
}

- (void)dealloc
{
    [model release];
    [timer release];
    [super dealloc];
}

- (PyExtraFairwareReminder *)model
{
    return (PyExtraFairwareReminder *)model;
}

- (void)start
{
    [[self model] start];
}

- (void)updateButton
{
    [[self model] updateButton];
}

- (IBAction)continue:(id)sender
{
    [NSApp stopModal];
}

- (IBAction)contribute:(id)sender
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://open.hardcoded.net/contribute/"]];
}

/* Model --> View */
- (void)startTimer
{
    timer = [[NSTimer timerWithTimeInterval:0.2 target:self selector:@selector(updateButton) 
        userInfo:nil repeats:YES] retain];
    // Needed for the timer to work in modal mode.
    [[NSRunLoop currentRunLoop] addTimer:timer forMode:NSModalPanelRunLoopMode];
}

- (void)stopTimer
{
    [timer invalidate];
}

- (void)setButtonText:(NSString *)text
{
    [continueButton setTitle:text];
}

- (void)enableButton
{
    [continueButton setEnabled:YES];
}
@end