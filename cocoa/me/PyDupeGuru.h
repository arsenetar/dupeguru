/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "../base/PyDupeGuru.h"

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
