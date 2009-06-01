#import <Cocoa/Cocoa.h>
#import "dgbase/AppDelegate.h"
#import "ResultWindow.h"
#import "DirectoryPanel.h"
#import "PyDupeGuru.h"

@interface AppDelegate : AppDelegateBase
{
    IBOutlet NSButton *presetsButton;
    IBOutlet NSPopUpButton *presetsPopup;
    IBOutlet ResultWindow *result;
    
    DirectoryPanel *_directoryPanel;
}
- (IBAction)openWebsite:(id)sender;
- (IBAction)popupPresets:(id)sender;
- (IBAction)toggleDirectories:(id)sender;
- (IBAction)usePreset:(id)sender;

- (DirectoryPanel *)directoryPanel;
- (PyDupeGuru *)py;
@end
