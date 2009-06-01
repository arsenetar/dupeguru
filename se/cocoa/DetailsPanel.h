#import <Cocoa/Cocoa.h>
#import "cocoalib/PyApp.h"
#import "cocoalib/Table.h"


@interface DetailsPanel : NSWindowController
{
    IBOutlet TableView *detailsTable;
}
- (id)initWithPy:(PyApp *)aPy;

- (void)refresh;
@end