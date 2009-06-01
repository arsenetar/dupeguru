#import <Cocoa/Cocoa.h>
#import "dgbase/AppDelegate.h"
#import "ResultWindow.h"
#import "DirectoryPanel.h"
#import "DetailsPanel.h"
#import "PyDupeGuru.h"

@interface AppDelegate : AppDelegateBase
{
    IBOutlet ResultWindow *result;
    
    DetailsPanel *_detailsPanel;
    DirectoryPanel *_directoryPanel;
}
- (IBAction)openWebsite:(id)sender;
- (IBAction)toggleDetailsPanel:(id)sender;
- (IBAction)toggleDirectories:(id)sender;

- (DirectoryPanel *)directoryPanel;
- (PyDupeGuru *)py;
@end
