#import <Cocoa/Cocoa.h>
#import "dgbase/PyDupeGuru.h"

@interface PyDupeGuru : PyDupeGuruBase
//Scanning options
- (void)setScanType:(NSNumber *)scan_type;
- (void)setWordWeighting:(NSNumber *)words_are_weighted;
- (void)setMatchSimilarWords:(NSNumber *)match_similar_words;
@end
