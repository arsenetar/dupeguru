/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import <Quartz/Quartz.h>
#import "StatsLabel.h"
#import "ResultTable.h"
#import "ProblemDialog.h"
#import "HSTableView.h"
#import "PyDupeGuru.h"

@class AppDelegateBase;

@interface ResultWindowBase : NSWindowController
{
@protected
    IBOutlet NSSegmentedControl *optionsSwitch;
    IBOutlet HSTableView *matches;
    IBOutlet NSTextField *stats;
    IBOutlet NSSearchField *filterField;
    
    AppDelegateBase *app;
    PyDupeGuru *model;
    NSMenu *columnsMenu;
    ResultTable *table;
    StatsLabel *statsLabel;
    ProblemDialog *problemDialog;
    QLPreviewPanel* previewPanel;
}
- (id)initWithParentApp:(AppDelegateBase *)app;

/* Virtual */
- (void)initResultColumns;
- (void)setScanOptions;

/* Helpers */
- (void)fillColumnsMenu;
- (void)sendMarkedToTrash:(BOOL)hardlinkDeleted;
- (void)updateOptionSegments;
- (void)showProblemDialog;

/* Actions */
- (IBAction)changeOptions:(id)sender;
- (IBAction)copyMarked:(id)sender;
- (IBAction)deleteMarked:(id)sender;
- (IBAction)hardlinkMarked:(id)sender;
- (IBAction)exportToXHTML:(id)sender;
- (IBAction)filter:(id)sender;
- (IBAction)ignoreSelected:(id)sender;
- (IBAction)invokeCustomCommand:(id)sender;
- (IBAction)markAll:(id)sender;
- (IBAction)markInvert:(id)sender;
- (IBAction)markNone:(id)sender;
- (IBAction)markSelected:(id)sender;
- (IBAction)moveMarked:(id)sender;
- (IBAction)openClicked:(id)sender;
- (IBAction)openSelected:(id)sender;
- (IBAction)removeMarked:(id)sender;
- (IBAction)removeSelected:(id)sender;
- (IBAction)renameSelected:(id)sender;
- (IBAction)reprioritizeResults:(id)sender;
- (IBAction)resetColumnsToDefault:(id)sender;
- (IBAction)revealSelected:(id)sender;
- (IBAction)saveResults:(id)sender;
- (IBAction)startDuplicateScan:(id)sender;
- (IBAction)switchSelected:(id)sender;
- (IBAction)toggleColumn:(id)sender;
- (IBAction)toggleDelta:(id)sender;
- (IBAction)toggleDetailsPanel:(id)sender;
- (IBAction)togglePowerMarker:(id)sender;
- (IBAction)toggleQuicklookPanel:(id)sender;
@end
