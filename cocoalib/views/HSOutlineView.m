/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "HSOutlineView.h"

@implementation HSOutlineView
- (id <HSOutlineViewDelegate>)delegate
{
    return (id <HSOutlineViewDelegate>)[super delegate];
}

- (void)setDelegate:(id <HSOutlineViewDelegate>)aDelegate
{
    [super setDelegate:aDelegate];
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(outlineViewWasDoubleClicked:)]) {
        [self setTarget:[self delegate]];
        [self setDoubleAction:@selector(outlineViewWasDoubleClicked:)];
    }
}
/* NSOutlineView overrides */
- (void)keyDown:(NSEvent *)event 
{
    if (![self dispatchSpecialKeys:event])
    {
        [super keyDown:event];
    }
}

- (BOOL)shouldEditTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    BOOL result = [super shouldEditTableColumn:column row:row];
    if (!result)
        return result;
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(outlineView:shouldEditTableColumn:item:)])
        return [delegate outlineView:self shouldEditTableColumn:column item:[self itemAtRow:row]];
    return YES;
}

/* Notifications & Delegate */
- (void)textDidEndEditing:(NSNotification *)notification
{
    notification = [self processTextDidEndEditing:notification];
    NSView *nextKeyView = [self nextKeyView];
    [self setNextKeyView:nil];
    [super textDidEndEditing:notification];
    [self setNextKeyView:nextKeyView];
    
    if ([self editedColumn] == -1)
    {
        if (!manualEditionStop)
        {
            id delegate = [self delegate];
            if ([delegate respondsToSelector:@selector(outlineViewDidEndEditing:)])
            {
                [delegate outlineViewDidEndEditing:self];
            }
        }
        // We may have lost the focus
        [[self window] makeFirstResponder:self];
    }
}

- (BOOL)textView:(NSTextView *)textView doCommandBySelector:(SEL)command
{
    if (command == @selector(cancelOperation:))
    {
        [self stopEditing]; // The stop editing has to happen before the cancelEdits
        id delegate = [self delegate];
        if ([delegate respondsToSelector:@selector(outlineViewCancelsEdition:)])
        {
            [delegate outlineViewCancelsEdition:self];
        }
        return YES;
    }
    return NO;
}

/* Public */
- (NSIndexPath *)selectedPath
{
    NSInteger row = [self selectedRow];
    return [self itemAtRow:row];
}

- (void)selectPath:(NSIndexPath *)aPath
{
    [self selectNodePaths:[NSArray arrayWithObject:aPath]];
}

- (NSArray *)selectedNodePaths
{
    NSMutableArray *r = [NSMutableArray array];
    NSIndexSet *indexes = [self selectedRowIndexes];
    NSInteger i = [indexes firstIndex];
    while (i != NSNotFound) {
        NSIndexPath *path = [self itemAtRow:i];
        [r addObject:path];
        i = [indexes indexGreaterThanIndex:i];
    }
    return r;
}

- (void)selectNodePaths:(NSArray *)aPaths
{
    NSMutableIndexSet *toSelect = [NSMutableIndexSet indexSet];
    /* To ensure that we have correct row indexes, we must first expand all paths, and *then* select
     * row indexes.
    **/
    for (NSIndexPath *path in aPaths) {
        [self ensureExpanded:path];
    }
    for (NSIndexPath *path in aPaths) {
        [toSelect addIndex:[self rowForItem:path]];
    }
    [self selectRowIndexes:toSelect byExtendingSelection:NO];
    if ([toSelect count] > 0) {
        [self scrollRowToVisible:[toSelect firstIndex]];
    }
}

- (void)ensureExpanded:(NSIndexPath *)aPath
{
    /* Expands aPath and make sure that its parent items are expanded as well.
    */
    id <HSOutlineViewDelegate> delegate = [self delegate];
    NSIndexPath *tmppath = [NSIndexPath indexPathWithIndex:[aPath indexAtPosition:0]];
    for (NSInteger i=1; i<[aPath length]; i++) {
        [self expandItem:[delegate internalizedPath:tmppath]];
        tmppath = [tmppath indexPathByAddingIndex:[aPath indexAtPosition:i]];
    }
}

- (void)stopEditing
{
    // If we're not editing, don't do anything because we don't want to steal focus from another view
    if ([self editedColumn] >= 0)
    {
        manualEditionStop = YES;
        [[self window] makeFirstResponder:self]; // This will abort edition
        manualEditionStop = NO;
    }
}

- (void)updateSelection
{
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(selectedIndexPaths)]) {
        [self selectNodePaths:[delegate selectedIndexPaths]];
    }
}

/* Actions */

- (IBAction)copy:(id)sender
{
    NSString *data = [[self delegate] dataForCopyToPasteboard];
    if (data != nil) {
        NSPasteboard *p = [NSPasteboard generalPasteboard];
        [p declareTypes:[NSArray arrayWithObjects:NSStringPboardType, nil] owner:nil];
        [p setString:data forType:NSStringPboardType];
    }
}

/* BIG HACK ZONE
When tracking clicks in the NSTextField, the NSTableView goes in edition mode even if we click on the
arrow or the button. The only way I found to avoid this is this scheme: let the HSOutlineView know
of the event that caused the click, and don't go in edit mode if it happens.
*/

- (void)ignoreEventForEdition:(NSEvent *)aEvent
{
    eventToIgnore = aEvent;
}

- (void)editColumn:(NSInteger)columnIndex row:(NSInteger)rowIndex withEvent:(NSEvent *)theEvent select:(BOOL)flag
{
    if ((theEvent != nil) && (theEvent == eventToIgnore))
        return;
    [super editColumn:columnIndex row:rowIndex withEvent:theEvent select:flag];
}

@end
