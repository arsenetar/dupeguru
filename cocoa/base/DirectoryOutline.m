/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "DirectoryOutline.h"

@implementation DirectoryOutline
- (id)initWithPyRef:(PyObject *)aPyRef outlineView:(HSOutlineView *)aOutlineView
{
    self = [super initWithPyRef:aPyRef wrapperClass:[PyDirectoryOutline class]
        callbackClassName:@"DirectoryOutlineView" view:aOutlineView];
    [[self view] registerForDraggedTypes:[NSArray arrayWithObject:NSFilenamesPboardType]];
    return self;
}

- (PyDirectoryOutline *)model
{
    return (PyDirectoryOutline *)model;
}

/* Delegate */
- (NSDragOperation)outlineView:(NSOutlineView *)outlineView validateDrop:(id < NSDraggingInfo >)info proposedItem:(id)item proposedChildIndex:(NSInteger)index
{
    NSPasteboard *pboard;
    NSDragOperation sourceDragMask;
    sourceDragMask = [info draggingSourceOperationMask];
    pboard = [info draggingPasteboard];
    if ([[pboard types] containsObject:NSFilenamesPboardType]) {
        if (sourceDragMask & NSDragOperationLink)
            return NSDragOperationLink;
    }
    return NSDragOperationNone;    
}

- (BOOL)outlineView:(NSOutlineView *)outlineView acceptDrop:(id < NSDraggingInfo >)info item:(id)item childIndex:(NSInteger)index
{
    NSPasteboard *pboard;
    NSDragOperation sourceDragMask; 
    sourceDragMask = [info draggingSourceOperationMask];
    pboard = [info draggingPasteboard];
    if ([[pboard types] containsObject:NSFilenamesPboardType]) {
        NSArray *foldernames = [pboard propertyListForType:NSFilenamesPboardType];
        if (!(sourceDragMask & NSDragOperationLink))
            return NO;
        for (NSString *foldername in foldernames) {
            [[self model] addDirectory:foldername];
        }
        NSDictionary *userInfo = [NSDictionary dictionaryWithObject:foldernames forKey:@"foldernames"];
        [[NSNotificationCenter defaultCenter] postNotificationName:DGAddedFoldersNotification
            object:self userInfo:userInfo];
    }
    return YES;
}

- (void)outlineView:(NSOutlineView *)aOutlineView willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)tableColumn item:(id)item
{ 
    if ([cell isKindOfClass:[NSTextFieldCell class]]) {
        NSTextFieldCell *textCell = cell;
        NSIndexPath *path = item;
        BOOL selected = [path isEqualTo:[[self view] selectedPath]];
        if (selected) {
            [textCell setTextColor:[NSColor blackColor]];
            return;
        }
        NSInteger state = [self intProperty:@"state" valueAtPath:path];
        if (state == 1) {
            [textCell setTextColor:[NSColor blueColor]];
        }
        else if (state == 2) {
            [textCell setTextColor:[NSColor redColor]];
        }
        else {
            [textCell setTextColor:[NSColor blackColor]];
        }
    }
}
@end