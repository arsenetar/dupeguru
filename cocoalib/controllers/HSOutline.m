/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSOutline.h"
#import "Utils.h"

#define CHILDREN_COUNT_PROPERTY @"children_count"

@implementation HSOutline
- (id)initWithPyRef:(PyObject *)aPyRef wrapperClass:(Class)aWrapperClass callbackClassName:(NSString *)aCallbackClassName view:(HSOutlineView *)aView
{
    self = [super initWithPyRef:aPyRef wrapperClass:aWrapperClass callbackClassName:aCallbackClassName view:aView];
    itemData = [[NSMutableDictionary dictionary] retain];
    /* Dictionaries don't retain its keys because it copies them. Our items are NSIndexPath and when
    an index path has the same value, it's the same instance. Before OS X 10.7, all these instances
    stayed in memory, so we didn't need to worry about retaining them. Hoever, it seems now that
    index path instances are sometimes released. Oops. So, we now need to retain our index path
    instances and that's why we use itemRetainer.

    In fact, it seems that unlike what the doc says, it's not true that two index paths with the
    same value will always be the same instance.
    */
    itemRetainer = [[NSMutableSet set] retain];
    if (([[self view] outlineTableColumn] == nil) && ([[[self view] tableColumns] count] > 0)) {
        [[self view] setOutlineTableColumn:[[[self view] tableColumns] objectAtIndex:0]];
    }
    return self;
}

- (void)dealloc
{
    [itemData release];
    [itemRetainer release];
    [super dealloc];
}

- (HSOutlineView *)view
{
    return (HSOutlineView *)view;
}

- (void)setView:(HSOutlineView *)aOutlineView
{
    if ([self view] != nil) {
        [[self view] setDataSource:nil];
        [[self view] setDelegate:nil];
    }
    [super setView:aOutlineView];
    if (aOutlineView != nil) {
        [aOutlineView setDataSource:self];
        [aOutlineView setDelegate:self];
    }
}

- (PyOutline *)model
{
    return (PyOutline *)model;
}

/* Private */
- (void)setPySelection
{
    NSMutableArray *paths = [NSMutableArray array];
    NSIndexSet *indexes = [[self view] selectedRowIndexes];
    NSInteger i = [indexes firstIndex];
    while (i != NSNotFound) {
        NSIndexPath *path = [[self view] itemAtRow:i];
        [paths addObject:p2a(path)];
        i = [indexes indexGreaterThanIndex:i];
    }
    [[self model] setSelectedPaths:paths];
}

- (NSIndexPath *)internalizedPath:(NSIndexPath *)path
{
    /* Because NSIndexPath stopped guaranteeing that the same paths always were represented by the
       same instances, we have to make sure, when we manipulate paths, that we manipulate the same
       instances as those that were given by outlineView:child:ofItem:
    */
    NSIndexPath *result = [itemRetainer member:path];
    if (result == nil) {
        result = path;
        [itemData setObject:[NSMutableDictionary dictionary] forKey:result];
        [itemRetainer addObject:result];
    }
    return result;
}

/* Public */
- (void)refresh
{
    [itemData removeAllObjects];
    // We can't get rid of our instances just yet, we have to wait until after reloadData
    NSSet *oldRetainer = itemRetainer;
    itemRetainer = [[NSMutableSet set] retain];
    [[self view] setDelegate:nil];
    [[self view] reloadData];
    [[self view] setDelegate:self];
    /* Item retainer and releasing
    
    In theory, [oldRetainer release] should work, but in practice, doing so causes occasional
    crashes during drag & drop, which I guess keep the reference of an item a bit longer than it
    should. This is why we autorelease here. See #354.
    */
    [oldRetainer autorelease];
    [self updateSelection];
}

- (NSArray *)selectedIndexPaths
{
    NSArray *arrayPaths = [[self model] selectedPaths];
    NSMutableArray *result = [NSMutableArray array];
    for (NSArray *arrayPath in arrayPaths) {
        [result addObject:[self internalizedPath:a2p(arrayPath)]];
    }
    return result;
}

- (void)startEditing
{
    [[self view] startEditing];
}

- (void)stopEditing
{
    [[self view] stopEditing];
}

- (void)updateSelection
{
    [[self view] updateSelection];
}

- (void)expandItem:(NSIndexPath *)item
{
    [[self view] ensureExpanded:item];
}

/* Caching */
- (id)property:(NSString *)property valueAtPath:(NSIndexPath *)path
{
    NSMutableDictionary *props = [itemData objectForKey:path];
    id value = [props objectForKey:property];
    if (value == nil) {
        value = [[self model] property:property valueAtPath:p2a(path)];
        if (value == nil) {
            value = [NSNull null];
        }
        [props setObject:value forKey:property];
    }
    if (value == [NSNull null]) {
        value = nil;
    }
    return value;
}

- (void)setProperty:(NSString *)property value:(id)value atPath:(NSIndexPath *)path
{
    NSMutableDictionary *props = [itemData objectForKey:path];
    [props removeObjectForKey:property];
    [[self model] setProperty:property value:value atPath:p2a(path)];
}

- (NSString *)stringProperty:(NSString *)property valueAtPath:(NSIndexPath *)path
{
    return [self property:property valueAtPath:path];
}

- (void)setStringProperty:(NSString *)property value:(NSString *)value atPath:(NSIndexPath *)path
{
    [self setProperty:property value:value atPath:path];
}

- (BOOL)boolProperty:(NSString *)property valueAtPath:(NSIndexPath *)path
{
    NSNumber *value = [self property:property valueAtPath:path];
    return [value boolValue];
}

- (void)setBoolProperty:(NSString *)property value:(BOOL)value atPath:(NSIndexPath *)path
{
    [self setProperty:property value:[NSNumber numberWithBool:value] atPath:path];
}

- (NSInteger)intProperty:(NSString *)property valueAtPath:(NSIndexPath *)path
{
    NSNumber *value = [self property:property valueAtPath:path];
    return [value intValue];
}

- (void)setIntProperty:(NSString *)property value:(int)value atPath:(NSIndexPath *)path
{
    [self setProperty:property value:[NSNumber numberWithInt:value] atPath:path];
}

- (void)refreshItemAtPath:(NSIndexPath *)path
{
    NSMutableDictionary *props = [itemData objectForKey:path];
    [props removeAllObjects];
}

/* NSOutlineView data source */

- (NSInteger)outlineView:(NSOutlineView *)outlineView numberOfChildrenOfItem:(id)item
{
    return [self intProperty:CHILDREN_COUNT_PROPERTY valueAtPath:(NSIndexPath *)item];
}

- (id)outlineView:(NSOutlineView *)outlineView child:(NSInteger)index ofItem:(id)item
{
    NSIndexPath *parent = item;
    NSIndexPath *path = parent == nil ? [NSIndexPath indexPathWithIndex:index] : [parent indexPathByAddingIndex:index];
    return [self internalizedPath:path];
}

- (BOOL)outlineView:(NSOutlineView *)theOutlineView isItemExpandable:(id)item
{
    return [self outlineView:[self view] numberOfChildrenOfItem:item] > 0;
}

- (BOOL)outlineView:(NSOutlineView *)outlineView shouldEditTableColumn:(NSTableColumn *)column item:(id)item
{
    return [[self model] canEditProperty:[column identifier] atPath:p2a((NSIndexPath *)item)];
}

- (id)outlineView:(NSOutlineView *)outlineView objectValueForTableColumn:(NSTableColumn *)column byItem:(id)item
{
    return [self property:[column identifier] valueAtPath:(NSIndexPath *)item];
}

- (void)outlineView:(NSOutlineView *)outlineView setObjectValue:(id)value forTableColumn:(NSTableColumn *)column byItem:(id)item
{
    [self setProperty:[column identifier] value:value atPath:(NSIndexPath *)item];
}

/* We need to change the model selection at both IsChanging and DidChange. We need to set the
model selection at IsChanging before of the arrow clicking. The action launched by this little arrow
is performed before DidChange. However, when using the arrow to change the selection, IsChanging is
never called
*/
- (void)outlineViewSelectionIsChanging:(NSNotification *)notification
{
    [self setPySelection];
}

- (void)outlineViewSelectionDidChange:(NSNotification *)notification
{
    [self setPySelection];
}

/* HSOutlineView delegate */
- (NSIndexPath *)selectedIndexPath
{
    NSArray *paths = [self selectedIndexPaths];
    if ([paths count] > 0) {
        return [paths objectAtIndex:0];
    }
    else {
        return nil;
    }
}

- (NSString *)dataForCopyToPasteboard
{
    return nil;
}

- (void)outlineViewDidEndEditing:(HSOutlineView *)outlineView
{
    [[self model] saveEdits];
}

- (void)outlineViewWasDoubleClicked:(HSOutlineView *)outlineView
{
}

- (void)outlineViewCancelsEdition:(HSOutlineView *)outlineView
{
    [[self model] cancelEdits];
}
@end