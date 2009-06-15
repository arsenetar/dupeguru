#import <Cocoa/Cocoa.h>
#import "PyApp.h"
#import "Table.h"


@interface DetailsPanelBase : NSWindowController
{
    IBOutlet TableView *detailsTable;
}
- (id)initWithPy:(PyApp *)aPy;

- (void)refresh;

/* Notifications */
- (void)duplicateSelectionChanged:(NSNotification *)aNotification;
@end