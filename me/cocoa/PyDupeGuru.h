#import <Cocoa/Cocoa.h>
#import "dgbase/PyDupeGuru.h"

@interface PyDupeGuru : PyDupeGuruBase
//Scanning options
- (void)setScanType:(NSNumber *)scan_type;
- (void)setMinWordCount:(NSNumber *)word_count;
- (void)setMinWordLength:(NSNumber *)word_length;
- (void)setWordWeighting:(NSNumber *)words_are_weighted;
- (void)setMatchSimilarWords:(NSNumber *)match_similar_words;
- (void)enable:(NSNumber *)enable scanForTag:(NSString *)tag;
- (void)scanDeadTracks;
- (void)removeDeadTracks;
- (int)deadTrackCount;
@end
