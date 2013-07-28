/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import <Quartz/Quartz.h>
#import "HSTable.h"
#import "PyResultTable.h"

@interface ResultTable : HSTable <QLPreviewPanelDataSource, QLPreviewPanelDelegate>
{
}
- (id)initWithPyRef:(PyObject *)aPyRef view:(NSTableView *)aTableView;
- (PyResultTable *)model;
- (BOOL)powerMarkerMode;
- (void)setPowerMarkerMode:(BOOL)aPowerMarkerMode;
- (BOOL)deltaValuesMode;
- (void)setDeltaValuesMode:(BOOL)aDeltaValuesMode;
@end;