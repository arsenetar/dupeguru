#import <Cocoa/Cocoa.h>
#import "RecentDirectories.h"
#import "Outline.h"
#import "PyDupeGuru.h"

@interface DirectoryPanelBase : NSWindowController
{
    IBOutlet NSPopUpButton *addButtonPopUp;
    IBOutlet OutlineView *directories;
    IBOutlet NSButton *removeButton;
    
    PyDupeGuruBase *_py;
    RecentDirectories *_recentDirectories;
}
- (id)initWithParentApp:(id)aParentApp;

- (IBAction)askForDirectory:(id)sender;
- (IBAction)changeDirectoryState:(id)sender;
- (IBAction)popupAddDirectoryMenu:(id)sender;
- (IBAction)removeSelectedDirectory:(id)sender;
- (IBAction)toggleVisible:(id)sender;

- (void)addDirectory:(NSString *)directory;
- (void)refreshRemoveButtonText;
@end
