#import <Cocoa/Cocoa.h>
#import "dgbase/DetailsPanel.h"

@interface DetailsPanel : DetailsPanelBase
{
    IBOutlet NSImageView *dupeImage;
    IBOutlet NSProgressIndicator *dupeProgressIndicator;
    IBOutlet NSImageView *refImage;
    IBOutlet NSProgressIndicator *refProgressIndicator;
    
    PyApp *py;
    BOOL _needsRefresh;
    NSString *_dupePath;
    NSString *_refPath;
}
@end