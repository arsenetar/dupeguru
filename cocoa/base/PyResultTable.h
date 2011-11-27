/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyTable.h"

@interface PyResultTable : PyTable
- (BOOL)powerMarkerMode;
- (void)setPowerMarkerMode:(BOOL)aPowerMarkerMode;
- (BOOL)deltaValuesMode;
- (void)setDeltaValuesMode:(BOOL)aDeltaValuesMode;

- (NSString *)valueForRow:(NSInteger)rowIndex column:(NSString *)aColumn;
- (BOOL)renameSelected:(NSString *)aNewName;
- (void)sortBy:(NSString *)aIdentifier ascending:(BOOL)aAscending;
- (void)markSelected;
- (void)removeSelected;
- (NSInteger)selectedDupeCount;
- (NSString *)pathAtIndex:(NSInteger)index;
@end