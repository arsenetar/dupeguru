#import <Cocoa/Cocoa.h>
#import "cocoalib/Outline.h"
#import "dgbase/ResultWindow.h"
#import "DetailsPanel.h"
#import "DirectoryPanel.h"

@interface ResultWindow : ResultWindowBase
{
    IBOutlet NSPopUpButton *actionMenu;
    IBOutlet NSMenu *columnsMenu;
    IBOutlet NSSearchField *filterField;
    IBOutlet NSWindow *preferencesPanel;
    
    NSString *_lastAction;
    DetailsPanel *_detailsPanel;
    NSMutableArray *_resultColumns;
    NSMutableIndexSet *_deltaColumns;
}
- (IBAction)clearIgnoreList:(id)sender;
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
- (IBAction)removeDeadTracks:(id)sender;
- (IBAction)removeMarked:(id)sender;
- (IBAction)removeSelected:(id)sender;
- (IBAction)renameSelected:(id)sender;
- (IBAction)resetColumnsToDefault:(id)sender;
- (IBAction)revealSelected:(id)sender;
- (IBAction)showPreferencesPanel:(id)sender;
- (IBAction)startDuplicateScan:(id)sender;
- (IBAction)toggleColumn:(id)sender;
- (IBAction)toggleDelta:(id)sender;
- (IBAction)toggleDetailsPanel:(id)sender;

- (NSTableColumn *)getColumnForIdentifier:(int)aIdentifier title:(NSString *)aTitle width:(int)aWidth refCol:(NSTableColumn *)aColumn;
- (NSArray *)getColumnsOrder;
- (NSDictionary *)getColumnsWidth;
- (void)initResultColumns;
- (void)restoreColumnsPosition:(NSArray *)aColumnsOrder widths:(NSDictionary *)aColumnsWidth;
@end
