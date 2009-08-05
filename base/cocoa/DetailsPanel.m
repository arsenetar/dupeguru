/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "DetailsPanel.h"
#import "Consts.h"

@implementation DetailsPanelBase
- (id)initWithPy:(PyApp *)aPy
{
    self = [super initWithWindowNibName:@"Details"];
    [self window]; //So the detailsTable is initialized.
    [detailsTable setPy:aPy];
	[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(duplicateSelectionChanged:) name:DuplicateSelectionChangedNotification object:nil];
    return self;
}

- (void)refresh
{
    [detailsTable reloadData];
}

/* Notifications */
- (void)duplicateSelectionChanged:(NSNotification *)aNotification
{
    if ([[self window] isVisible])
        [self refresh];
}
@end
