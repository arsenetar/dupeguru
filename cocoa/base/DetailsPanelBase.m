/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "DetailsPanelBase.h"
#import "HSPyUtil.h"

@implementation DetailsPanelBase

@synthesize detailsTable;

- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithWindow:nil];
    [self setWindow:[self createWindow]];
    model = [[PyDetailsPanel alloc] initWithModel:aPyRef];
    [model bindCallback:createCallback(@"DetailsPanelView", self)];
    return self;
}

- (void)dealloc
{
    [model release];
    [super dealloc];
}

- (PyDetailsPanel *)model
{
    return (PyDetailsPanel *)model;
}

- (NSWindow *)createWindow
{
    return nil; // Virtual
}

- (void)refreshDetails
{
    [detailsTable reloadData];
}

- (BOOL)isVisible
{
    return [[self window] isVisible];
}

- (void)toggleVisibility
{
    if ([self isVisible]) {
        [[self window] close];
    }
    else {
        [self refreshDetails]; // selection might have changed since last time
        [[self window] orderFront:nil];
    }
}

/* NSTableView Delegate */
- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView
{
    return [[self model] numberOfRows];
}

- (id)tableView:(NSTableView *)tableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    return [[self model] valueForColumn:[column identifier] row:row];
}

/* Python --> Cocoa */
- (void)refresh
{
    if ([[self window] isVisible]) {
        [self refreshDetails];
    }
}
@end
