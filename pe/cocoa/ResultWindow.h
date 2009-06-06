#import <Cocoa/Cocoa.h>
#import "Outline.h"
#import "dgbase/ResultWindow.h"
#import "DirectoryPanel.h"

@interface ResultWindow : ResultWindowBase
{
    IBOutlet NSPopUpButton *actionMenu;
    IBOutlet NSMenu *columnsMenu;
    IBOutlet NSSearchField *filterField;
    IBOutlet NSSegmentedControl *pmSwitch;
    IBOutlet NSWindow *preferencesPanel;
    IBOutlet NSTextField *stats;
    
    NSMutableArray *_resultColumns;
    NSMutableIndexSet *_deltaColumns;
}
- (IBAction)changePowerMarker:(id)sender;
- (IBAction)clearIgnoreList:(id)sender;
- (IBAction)clearPictureCache:(id)sender;
- (IBAction)exportToXHTML:(id)sender;
- (IBAction)filter:(id)sender;
- (IBAction)ignoreSelected:(id)sender;
- (IBAction)markAll:(id)sender;
- (IBAction)markInvert:(id)sender;
- (IBAction)markNone:(id)sender;
- (IBAction)markSelected:(id)sender;
- (IBAction)markToggle:(id)sender;
- (IBAction)openSelected:(id)sender;
- (IBAction)refresh:(id)sender;
- (IBAction)removeMarked:(id)sender;
- (IBAction)removeSelected:(id)sender;
- (IBAction)renameSelected:(id)sender;
- (IBAction)resetColumnsToDefault:(id)sender;
- (IBAction)revealSelected:(id)sender;
- (IBAction)showPreferencesPanel:(id)sender;
- (IBAction)startDuplicateScan:(id)sender;
- (IBAction)switchSelected:(id)sender;
- (IBAction)toggleColumn:(id)sender;
- (IBAction)toggleDelta:(id)sender;
- (IBAction)toggleDetailsPanel:(id)sender;
- (IBAction)togglePowerMarker:(id)sender;
- (IBAction)toggleDirectories:(id)sender;

- (NSTableColumn *)getColumnForIdentifier:(int)aIdentifier title:(NSString *)aTitle width:(int)aWidth refCol:(NSTableColumn *)aColumn;
- (NSArray *)getColumnsOrder;
- (NSDictionary *)getColumnsWidth;
- (NSArray *)getSelected:(BOOL)aDupesOnly;
- (NSArray *)getSelectedPaths:(BOOL)aDupesOnly;
- (void)performPySelection:(NSArray *)aIndexPaths;
- (void)initResultColumns;
- (void)refreshStats;
- (void)restoreColumnsPosition:(NSArray *)aColumnsOrder widths:(NSDictionary *)aColumnsWidth;
@end
