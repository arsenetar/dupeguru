/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "dgbase/PyDupeGuru.h"

@interface PyDupeGuru : PyDupeGuruBase
//Scanning options
- (void)setScanType:(NSNumber *)scan_type;
- (void)setWordWeighting:(NSNumber *)words_are_weighted;
- (void)setMatchSimilarWords:(NSNumber *)match_similar_words;
@end
