/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "DetailsPanel.h"
#import "Utils.h"

@implementation DetailsPanel
- (id)init
{
    self = [super initWithWindowNibName:@"DetailsPanel"];
    [self window]; //So the detailsTable is initialized.
    py = [[PyDetailsPanel alloc] initWithModel:findHackishModel(@"details_panel")];
    [py bindCallback:createCallback(@"DetailsPanelView", self)];
    [py connect];
    return self;
}

- (void)dealloc
{
    [py disconnect];
    [py release];
    [super dealloc];
}

- (PyDetailsPanel *)py
{
    return (PyDetailsPanel *)py;
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
    return [[self py] numberOfRows];
}

- (id)tableView:(NSTableView *)tableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    return [[self py] valueForColumn:[column identifier] row:row];
}

/* Python --> Cocoa */
- (void)refresh
{
    if ([[self window] isVisible]) {
        [self refreshDetails];
    }
}
@end
