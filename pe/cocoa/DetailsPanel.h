#import <Cocoa/Cocoa.h>
#import "PyApp.h"
#import "Table.h"


@interface DetailsPanel : NSWindowController
{
    IBOutlet TableView *detailsTable;
    IBOutlet NSImageView *dupeImage;
    IBOutlet NSProgressIndicator *dupeProgressIndicator;
    IBOutlet NSImageView *refImage;
    IBOutlet NSProgressIndicator *refProgressIndicator;
    
    PyApp *py;
    BOOL _needsRefresh;
    NSString *_dupePath;
    NSString *_refPath;
}
- (id)initWithPy:(PyApp *)aPy;
- (void)refresh;
@end