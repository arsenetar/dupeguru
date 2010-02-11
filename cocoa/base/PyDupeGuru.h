/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyApp.h"

@interface PyDupeGuruBase : PyApp
//Actions
- (NSNumber *)addDirectory:(NSString *)name;
- (void)removeDirectory:(NSNumber *)index;
- (void)loadResults;
- (void)saveResults;
- (void)loadIgnoreList;
- (void)saveIgnoreList;
- (void)clearIgnoreList;
- (void)purgeIgnoreList;
- (NSString *)exportToXHTMLwithColumns:(NSArray *)aColIds;

- (NSNumber *)doScan;

- (NSArray *)selectedPowerMarkerNodePaths;
- (void)selectPowerMarkerNodePaths:(NSArray *)aIndexPaths;
- (NSArray *)selectedResultNodePaths;
- (void)selectResultNodePaths:(NSArray *)aIndexPaths;

- (void)toggleSelectedMark;
- (void)markAll;
- (void)markInvert;
- (void)markNone;

- (void)addSelectedToIgnoreList;
- (void)removeSelected;
- (void)openSelected;
- (void)revealSelected;
- (void)makeSelectedReference;
- (void)applyFilter:(NSString *)filter;

- (void)sortGroupsBy:(NSNumber *)aIdentifier ascending:(NSNumber *)aAscending;
- (void)sortDupesBy:(NSNumber *)aIdentifier ascending:(NSNumber *)aAscending;

- (void)copyOrMove:(NSNumber *)aCopy markedTo:(NSString *)destination recreatePath:(NSNumber *)aRecreateType;
- (void)deleteMarked;
- (void)removeMarked;

//Data
- (NSNumber *)getIgnoreListCount;
- (NSNumber *)getMarkCount;
- (NSString *)getStatLine;
- (NSNumber *)getOperationalErrorCount;

//Scanning options
- (void)setMinMatchPercentage:(NSNumber *)percentage;
- (void)setMixFileKind:(NSNumber *)mix_file_kind;
- (void)setDisplayDeltaValues:(NSNumber *)display_delta_values;
- (void)setEscapeFilterRegexp:(NSNumber *)escape_filter_regexp;
- (void)setRemoveEmptyFolders:(NSNumber *)remove_empty_folders;
- (void)setSizeThreshold:(NSInteger)size_threshold;
@end
