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
