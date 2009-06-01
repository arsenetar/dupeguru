#import <Cocoa/Cocoa.h>
#import "dgbase/AppDelegate.h"
#import "ResultWindow.h"
#import "DirectoryPanel.h"
#import "PyDupeGuru.h"

@interface AppDelegate : AppDelegateBase
{
    IBOutlet ResultWindow *result;
    
    DirectoryPanel *_directoryPanel;
}
- (IBAction)openWebsite:(id)sender;
- (IBAction)toggleDirectories:(id)sender;

- (DirectoryPanel *)directoryPanel;
- (PyDupeGuru *)py;
@end
