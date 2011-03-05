/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ExtraFairwareReminder.h"

@implementation ExtraFairwareReminder
- (id)initWithPy:(PyApp *)aPy
{
    self = [super initWithNibName:@"ExtraFairwareReminder" pyClassName:@"PyExtraFairwareReminder" pyParent:aPy];
    [self window];
    [continueButton setEnabled:NO];
    return self;
}

- (void)dealloc
{
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