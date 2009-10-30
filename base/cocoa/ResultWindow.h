/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "Outline.h"
#import "DirectoryPanel.h"
#import "PyDupeGuru.h"

@interface MatchesView : OutlineView
- (void)keyDown:(NSEvent *)theEvent;
@end

@interface ResultWindowBase : NSWindowController
{
@protected
    IBOutlet PyDupeGuruBase *py;
    IBOutlet id app;
    IBOutlet NSSegmentedControl *deltaSwitch;
    IBOutlet MatchesView *matches;
	IBOutlet NSSegmentedControl *pmSwitch;
	IBOutlet NSTextField *stats;
	IBOutlet NSMenu *columnsMenu;
    
    BOOL _powerMode;
    BOOL _displayDelta;
    NSMutableArray *_resultColumns;
    NSWindowController *preferencesPanel;
}
/* Helpers */
- (void)fillColumnsMenu;
- (NSTableColumn *)getColumnForIdentifier:(int)aIdentifier title:(NSString *)aTitle width:(int)aWidth refCol:(NSTableColumn *)aColumn;
- (NSArray *)getColumnsOrder;
- (NSDictionary *)getColumnsWidth;
- (NSArray *)getSelected:(BOOL)aDupesOnly;
- (NSArray *)getSelectedPaths:(BOOL)aDupesOnly;
- (void)initResultColumns;
- (void)updatePySelection;
- (void)performPySelection:(NSArray *)aIndexPaths;
- (void)refreshStats;
- (void)restoreColumnsPosition:(NSArray *)aColumnsOrder widths:(NSDictionary *)aColumnsWidth;

/* Actions */
- (IBAction)changeDelta:(id)sender;
- (IBAction)changePowerMarker:(id)sender;
- (IBAction)copyMarked:(id)sender;
- (IBAction)deleteMarked:(id)sender;
- (IBAction)expandAll:(id)sender;
- (IBAction)exportToXHTML:(id)sender;
- (IBAction)moveMarked:(id)sender;
- (IBAction)resetColumnsToDefault:(id)sender;
- (IBAction)showPreferencesPanel:(id)sender;
- (IBAction)switchSelected:(id)sender;
- (IBAction)toggleColumn:(id)sender;
- (IBAction)togglePowerMarker:(id)sender;

/* Notifications */
- (void)jobCompleted:(NSNotification *)aNotification;
@end
