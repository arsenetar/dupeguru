/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "DeletionOptions.h"
#import "HSPyUtil.h"

@implementation DeletionOptions
- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithWindowNibName:@"DeletionOptions"];
    [self window];
    model = [[PyDeletionOptions alloc] initWithModel:aPyRef];
    [model bindCallback:createCallback(@"DeletionOptionsView", self)];
    return self;
}

- (void)dealloc
{
    [model release];
    [super dealloc];
}

- (IBAction)updateOptions:(id)sender
{
    [model setHardlink:[hardlinkButton state] == NSOnState];
    [model setDirect:[directButton state] == NSOnState];
}

- (IBAction)proceed:(id)sender
{
    [NSApp stopModalWithCode:NSOKButton];
}

- (IBAction)cancel:(id)sender
{
    [NSApp stopModalWithCode:NSCancelButton];
}

/* model --> view */
- (void)updateMsg:(NSString *)msg
{
    [messageTextField setStringValue:msg];
}

- (BOOL)show
{
    [hardlinkButton setState:NSOffState];
    [directButton setState:NSOffState];
    NSInteger r = [NSApp runModalForWindow:[self window]];
    [[self window] close];
    return r == NSOKButton;
}
@end