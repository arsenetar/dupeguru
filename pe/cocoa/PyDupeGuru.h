#import <Cocoa/Cocoa.h>
#import "dgbase/PyDupeGuru.h"

@interface PyDupeGuru : PyDupeGuruBase
- (void)clearPictureCache;
- (NSString *)getSelectedDupePath;
- (NSString *)getSelectedDupeRefPath;
- (void)setMatchScaled:(NSNumber *)match_scaled;
@end
