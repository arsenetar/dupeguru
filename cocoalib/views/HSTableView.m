/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "HSTableView.h"
#import "NSEventAdditions.h"

@implementation HSTableView
/* NSTableView */
- (void)keyDown:(NSEvent *)event 
{
    if (![self dispatchSpecialKeys:event]) {
        [super keyDown:event];
	}
}

- (id <HSTableViewDelegate>)delegate
{
    return (id <HSTableViewDelegate>)[super delegate];
}

- (void)setDelegate:(id <HSTableViewDelegate>)aDelegate
{
    [super setDelegate:aDelegate];
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(tableViewWasDoubleClicked:)]) {
        [self setTarget:[self delegate]];
        [self setDoubleAction:@selector(tableViewWasDoubleClicked:)];
    }
}

- (void)textDidEndEditing:(NSNotification *)notification
{
    notification = [self processTextDidEndEditing:notification];
    NSView *nextKeyView = [self nextKeyView];
    [self setNextKeyView:nil];
    [super textDidEndEditing:notification];
    [self setNextKeyView:nextKeyView];
    
	if ([self editedColumn] == -1) {
	    if (!manualEditionStop) {
	        id delegate = [self delegate];
	        if ([delegate respondsToSelector:@selector(tableViewDidEndEditing:)]) {
		        [delegate tableViewDidEndEditing:self];
	        }
	    }
        // We may have lost the focus
        [[self window] makeFirstResponder:self];
	}
}

/* NSTextView delegate */
- (BOOL)textView:(NSTextView *)textView doCommandBySelector:(SEL)command
{
    if (command == @selector(cancelOperation:)) {
        [self stopEditing]; // The stop editing has to happen before the cancelEdits
        id delegate = [self delegate];
        if ([delegate respondsToSelector:@selector(tableViewCancelsEdition:)]) {
	        [delegate tableViewCancelsEdition:self];
        }
        return YES;
    }
	return NO;
}

/* Public methods */

- (void)updateSelection
{
    NSIndexSet *selection = [[self delegate] selectedIndexes];
	[self selectRowIndexes:selection byExtendingSelection:NO];
}

// Calling this does not result in a tableViewDidEndEditing: call
- (void)stopEditing
{
    // If we're not editing, don't do anything because we don't want to steal focus from another view
    if ([self editedColumn] >= 0) {
        manualEditionStop = YES;
        [[self window] makeFirstResponder:self]; // This will abort edition
        manualEditionStop = NO;
    }
}

- (NSScrollView *)wrapInScrollView;
{
    /* When programmatically creating an NSTableView, we have to wrap it in a scroll view for it to
       behave properly.
    */
    NSScrollView *container = [[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, 100, 100)];
    [container setDocumentView:self];
    [container setHasVerticalScroller:YES];
    [container setHasHorizontalScroller:YES];
    [container setAutohidesScrollers:YES];
    return [container autorelease];
}

@end
