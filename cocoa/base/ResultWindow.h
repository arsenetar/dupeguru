/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import <Quartz/Quartz.h>
#import "StatsLabel.h"
#import "ResultTable.h"
#import "ProblemDialog.h"
#import "DeletionOptions.h"
#import "HSTableView.h"
#import "PyDupeGuru.h"

@class AppDelegateBase;

@interface ResultWindowBase : NSWindowController
{
@protected
    NSSegmentedControl *optionsSwitch;
    NSToolbarItem *optionsToolbarItem;
    HSTableView *matches;
    NSTextField *stats;
    NSSearchField *filterField;
    
    AppDelegateBase *app;
    PyDupeGuru *model;
    ResultTable *table;
    StatsLabel *statsLabel;
    ProblemDialog *problemDialog;
    DeletionOptions *deletionOptions;
    QLPreviewPanel* previewPanel;
}

@property (readwrite, retain) NSSegmentedControl *optionsSwitch;
@property (readwrite, retain) NSToolbarItem *optionsToolbarItem;
@property (readwrite, retain) HSTableView *matches;
@property (readwrite, retain) NSTextField *stats;
@property (readwrite, retain) NSSearchField *filterField;

- (id)initWithParentApp:(AppDelegateBase *)app;

/* Virtual */
- (void)initResultColumns;
- (void)setScanOptions;

/* Helpers */
- (void)fillColumnsMenu;
- (void)updateOptionSegments;
- (void)showProblemDialog;
- (void)adjustUIToLocalization;

/* Actions */
- (IBAction)changeOptions:(id)sender;
- (IBAction)copyMarked:(id)sender;
- (IBAction)trashMarked:(id)sender;
- (IBAction)exportToXHTML:(id)sender;
- (IBAction)filter:(id)sender;
- (IBAction)focusOnFilterField:(id)sender;
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
