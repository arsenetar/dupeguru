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
    IBOutlet NSView *actionMenuView;
    IBOutlet NSSegmentedControl *deltaSwitch;
    IBOutlet NSView *deltaSwitchView;
    IBOutlet NSView *filterFieldView;
    IBOutlet MatchesView *matches;
    IBOutlet NSView *pmSwitchView;
    
    BOOL _powerMode;
    BOOL _displayDelta;
}
- (NSString *)logoImageName;
/* Actions */
- (IBAction)changeDelta:(id)sender;
- (IBAction)copyMarked:(id)sender;
- (IBAction)deleteMarked:(id)sender;
- (IBAction)expandAll:(id)sender;
- (IBAction)moveMarked:(id)sender;
/* Notifications */
- (void)jobCompleted:(NSNotification *)aNotification;
@end
