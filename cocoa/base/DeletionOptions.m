/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "DeletionOptions.h"
#import "DeletionOptions_UI.h"
#import "HSPyUtil.h"

@implementation DeletionOptions

@synthesize messageTextField;
@synthesize linkButton;
@synthesize linkTypeRadio;
@synthesize directButton;

- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithWindow:nil];
    model = [[PyDeletionOptions alloc] initWithModel:aPyRef];
    [self setWindow:createDeletionOptions_UI(self)];
    [model bindCallback:createCallback(@"DeletionOptionsView", self)];
    return self;
}

- (void)dealloc
{
    [model release];
    [super dealloc];
}

- (void)updateOptions
{
    [model setLinkDeleted:[linkButton state] == NSOnState];
    [model setUseHardlinks:[linkTypeRadio selectedColumn] == 1];
    [model setDirect:[directButton state] == NSOnState];
}

- (void)proceed
{
    [NSApp stopModalWithCode:NSOKButton];
}

- (void)cancel
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
    [linkButton setState:NSOffState];
    [directButton setState:NSOffState];
    [linkTypeRadio selectCellAtRow:0 column:0];
    NSInteger r = [NSApp runModalForWindow:[self window]];
    [[self window] close];
    return r == NSOKButton;
}

- (void)setHardlinkOptionEnabled:(BOOL)enabled
{
    [linkTypeRadio setEnabled:enabled];
}
@end