/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "NSTableViewAdditions.h"
#import "NSEventAdditions.h"
#import "Utils.h"

@implementation NSTableView(NSTableViewAdditions)

/* Private methods */

// Alright, this is a hack. It has been added to put in common some table and outline code, but the
// thing is an outline view delegate doesn't use tableView:shouldEditTableColumn:row:. Anyway, for 
// the outline, just using [column isEditable] works in moneyGuru for now, so we can keep it that way.
- (BOOL)shouldEditTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    if (![column isEditable])
        return NO;
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(tableView:shouldEditTableColumn:row:)])
    {
        return [delegate tableView:self shouldEditTableColumn:column row:row];
    }
    else
    {
        return YES;
    }
}

/* Public Methods */

// Returns whether the responder chain should be stopeed or not
- (BOOL)dispatchSpecialKeys:(NSEvent *)event
{
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(tableView:receivedKeyEvent:)]) {
        if ([delegate tableView:self receivedKeyEvent:event]) {
            return YES;
        }
    }
    BOOL stopChain = NO;
    if ([event isDeleteOrBackspace] && [delegate respondsToSelector:@selector(tableViewHadDeletePressed:)])
	{
        stopChain = [delegate tableViewHadDeletePressed:self];
	}
    if ([event isReturnOrEnter] && [delegate respondsToSelector:@selector(tableViewHadReturnPressed:)])
	{
        stopChain = [delegate tableViewHadReturnPressed:self];
	}
	if ([event isSpace] && [delegate respondsToSelector:@selector(tableViewHadSpacePressed:)])
	{
        stopChain = [delegate tableViewHadSpacePressed:self];
	}
	if ([event isTab]) 
	{
		stopChain = YES;
		[[self window] makeFirstResponder:[self nextValidKeyView]];
	}
	if ([event isBackTab]) 
	{
		stopChain = YES;
		// Ok, this is a big hack. the normal handling of NSTableView must handle this, but we must skip over
		// a NSClipView and a NSScrollView before getting to the actual previousValidKeyView.
		// However, when we are not in Full Keyboard Access mode, there's no problem. Thus, we assume that
		// when previousValidKeyView's class is a NSClipView, it means we must perform the hack
        NSView *previous = [self previousValidKeyView];
        if ([[previous className] isEqualTo:@"NSClipView"]) // Can't use isKindOfClass, we don't want to test for a subclass
            previous = [[previous previousValidKeyView] previousValidKeyView];
        [[self window] makeFirstResponder:previous];
	}
    return stopChain;
}

- (NSNotification *)processTextDidEndEditing:(NSNotification *)notification;
{
    NSDictionary *userInfo = [notification userInfo];
	int textMovement = [[userInfo valueForKey:@"NSTextMovement"] intValue];
	if (textMovement == NSReturnTextMovement)
	{
	    // Stop editing
		NSMutableDictionary *newInfo;
        newInfo = [NSMutableDictionary dictionaryWithDictionary:userInfo];
        [newInfo setObject:[NSNumber numberWithInt:NSIllegalTextMovement] forKey:@"NSTextMovement"];
        notification = [NSNotification notificationWithName:[notification name] object:[notification object] userInfo:newInfo];
	}
    return notification;
}

- (void)startEditing
{
    // Make sure one row is selected
    if ([self selectedRow] == -1)
    {
        return;
    }
    
    // We only want to edit columns that are editable. If there aren't any, don't edit.
    for (NSInteger i=0;i<[[self tableColumns] count];i++) {
        NSTableColumn *col = [[self tableColumns] objectAtIndex:i];
        if ([col isHidden]) {
            continue;
        }
        if (![self shouldEditTableColumn:col row:[self selectedRow]]) {
            continue;
        }
        // We only want one row to be selected.
        NSIndexSet *selection = [NSIndexSet indexSetWithIndex:[self selectedRow]];
        [self selectRowIndexes:selection byExtendingSelection:NO];
    	[self editColumn:i row:[self selectedRow] withEvent:nil select:YES];
        break;
    }
}
@end
