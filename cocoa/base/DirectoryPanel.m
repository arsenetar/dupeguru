/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "DirectoryPanel.h"
#import "Dialogs.h"
#import "Utils.h"
#import "AppDelegate.h"

@implementation DirectoryOutline
- (void)doInit
{
    [super doInit];
    [self registerForDraggedTypes:[NSArray arrayWithObject:NSFilenamesPboardType]];
}

- (NSDragOperation)outlineView:(NSOutlineView *)outlineView validateDrop:(id < NSDraggingInfo >)info proposedItem:(id)item proposedChildIndex:(NSInteger)index
{
    NSPasteboard *pboard;
    NSDragOperation sourceDragMask;
    sourceDragMask = [info draggingSourceOperationMask];
    pboard = [info draggingPasteboard];
    if ([[pboard types] containsObject:NSFilenamesPboardType])
    {
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
    if ( [[pboard types] containsObject:NSFilenamesPboardType] )
    {
        NSArray *filenames = [pboard propertyListForType:NSFilenamesPboardType];
        if (!(sourceDragMask & NSDragOperationLink))
            return NO;
        if (([self delegate] == nil) || (![[self delegate] respondsToSelector:@selector(outlineView:addDirectory:)]))
            return NO;
        for (NSString *filename in filenames)
            [[self delegate] outlineView:self addDirectory:filename];
    }
    return YES;
}

@end

@implementation DirectoryPanel
- (id)initWithParentApp:(id)aParentApp
{
    self = [super initWithWindowNibName:@"DirectoryPanel"];
    [self window];
    AppDelegateBase *app = aParentApp;
    _py = [app py];
    _recentDirectories = [app recentDirectories];
    [directories setPy:_py];
    NSPopUpButtonCell *cell = [[directories tableColumnWithIdentifier:@"1"] dataCell];
    [cell addItemWithTitle:@"Normal"];
    [cell addItemWithTitle:@"Reference"];
    [cell addItemWithTitle:@"Excluded"];
    for (NSInteger i=0;i<[[cell itemArray] count];i++)
    {
        NSMenuItem *mi = [[cell itemArray] objectAtIndex:i];
        [mi setTarget:self];
        [mi setAction:@selector(changeDirectoryState:)];
        [mi setTag:i];
    }
    [self refreshRemoveButtonText];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(directorySelectionChanged:) name:NSOutlineViewSelectionDidChangeNotification object:directories];
    return self;
}

/* Actions */

- (IBAction)askForDirectory:(id)sender
{
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:YES];
    [op setCanChooseDirectories:YES];
    [op setAllowsMultipleSelection:NO];
    [op setTitle:@"Select a directory to add to the scanning list"];
    [op setDelegate:self];
    if ([op runModalForTypes:nil] == NSOKButton)
    {
        NSString *directory = [[op filenames] objectAtIndex:0];
        [self addDirectory:directory];
    }
}

- (IBAction)changeDirectoryState:(id)sender
{
    OVNode *node = [directories itemAtRow:[directories clickedRow]];
    [_py setDirectory:p2a([node indexPath]) state:i2n([sender tag])]; 
    [node resetAllBuffers];
    [directories reloadItem:node reloadChildren:YES];
    [directories display];
}

- (IBAction)popupAddDirectoryMenu:(id)sender
{
    if ([[_recentDirectories directories] count] == 0)
    {
        [self askForDirectory:sender];
        return;
    }
    NSMenu *m = [addButtonPopUp menu];
    while ([m numberOfItems] > 0)
        [m removeItemAtIndex:0];
    NSMenuItem *mi = [m addItemWithTitle:@"Add New Directory..." action:@selector(askForDirectory:) keyEquivalent:@""];
    [mi setTarget:self];
    [m addItem:[NSMenuItem separatorItem]];
    [_recentDirectories fillMenu:m];
    [addButtonPopUp selectItem:nil];
    [[addButtonPopUp cell] performClickWithFrame:[sender frame] inView:[sender superview]];
}

- (IBAction)removeSelectedDirectory:(id)sender
{
    [[self window] makeKeyAndOrderFront:nil];
    if ([directories selectedRow] < 0)
        return;
    OVNode *node = [directories itemAtRow:[directories selectedRow]];
    if ([node level] == 1)
    {
        [_py removeDirectory:i2n([node index])];
        [directories reloadData];
    }
    else
    {
        NSInteger state = n2i([[node buffer] objectAtIndex:1]);
        NSInteger newState = state == 2 ? 0 : 2; // If excluded, put it back
        [_py setDirectory:p2a([node indexPath]) state:i2n(newState)];
        [node resetAllBuffers];
        [directories display];
    }
    [self refreshRemoveButtonText];
}

- (IBAction)toggleVisible:(id)sender
{
    [[self window] makeKeyAndOrderFront:nil];
}

/* Public */

- (void)addDirectory:(NSString *)directory
{
    NSInteger r = [[_py addDirectory:directory] intValue];
    if (r)
    {
        NSString *m;
        switch (r)
        {
            case 1:
            {
                m = @"This directory already is in the list.";
                break;
            }
            case 2:
            {
                m = @"This directory does not exist.";
                break;
            }
        }
        [Dialogs showMessage:m];
    }
    [directories reloadData];
    [_recentDirectories addDirectory:directory];
    [[self window] makeKeyAndOrderFront:nil];
}

- (void)refreshRemoveButtonText
{
    if ([directories selectedRow] < 0)
    {
        [removeButton setEnabled:NO];
        return;
    }
    [removeButton setEnabled:YES];
    OVNode *node = [directories itemAtRow:[directories selectedRow]];
    NSInteger state = n2i([[node buffer] objectAtIndex:1]);
    NSString *buttonText = state == 2 ? @"Put Back" : @"Remove";
    [removeButton setTitle:buttonText];
}

/* Delegate */

- (void)outlineView:(NSOutlineView *)outlineView addDirectory:(NSString *)directory
{
    [self addDirectory:directory];
}

- (void)outlineView:(NSOutlineView *)outlineView willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)tableColumn item:(id)item
{ 
    OVNode *node = item;
    NSInteger state = n2i([[node buffer] objectAtIndex:1]);
    if ([cell isKindOfClass:[NSTextFieldCell class]])
    {
        NSTextFieldCell *textCell = cell;
        if (state == 1)
            [textCell setTextColor:[NSColor blueColor]];
        else if (state == 2)
            [textCell setTextColor:[NSColor redColor]];
        else
            [textCell setTextColor:[NSColor blackColor]];
    }
}

- (BOOL)panel:(id)sender shouldShowFilename:(NSString *)path
{
    BOOL isdir;
    [[NSFileManager defaultManager] fileExistsAtPath:path isDirectory:&isdir];
    return isdir;
}

/* Notifications */

- (void)directorySelectionChanged:(NSNotification *)aNotification
{
    [self refreshRemoveButtonText];
}

@end
