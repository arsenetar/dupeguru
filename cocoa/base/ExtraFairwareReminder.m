/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ExtraFairwareReminder.h"
#import "Utils.h"

@implementation ExtraFairwareReminder
- (id)init
{
    self = [super initWithWindowNibName:@"ExtraFairwareReminder"];
    [self window];
    [continueButton setEnabled:NO];
    py = [[PyExtraFairwareReminder alloc] initWithModel:findHackishModel(@"extra_fairware_reminder")];
    [py bindCallback:createCallback(@"ExtraFairwareReminderView", self)];
    return self;
}

- (void)dealloc
{
    [py release];
    [timer release];
    [super dealloc];
}

- (PyExtraFairwareReminder *)py
{
    return (PyExtraFairwareReminder *)py;
}

- (void)start
{
    [[self py] start];
}

- (void)updateButton
{
    [[self py] updateButton];
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