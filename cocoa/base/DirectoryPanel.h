/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSOutlineView.h"
#import "HSRecentFiles.h"
#import "DirectoryOutline.h"
#import "PyDupeGuru.h"

@class AppDelegateBase;

@interface DirectoryPanel : NSWindowController <NSOpenSavePanelDelegate>
{
    IBOutlet NSPopUpButton *addButtonPopUp;
    IBOutlet NSPopUpButton *loadRecentButtonPopUp;
    IBOutlet HSOutlineView *outlineView;
    IBOutlet NSButton *removeButton;
    
    AppDelegateBase *_app;
    PyDupeGuru *model;
    HSRecentFiles *_recentDirectories;
    DirectoryOutline *outline;
    BOOL _alwaysShowPopUp;
}
- (id)initWithParentApp:(AppDelegateBase *)aParentApp;

- (void)fillPopUpMenu; // Virtual

- (IBAction)askForDirectory:(id)sender;
- (IBAction)popupAddDirectoryMenu:(id)sender;
- (IBAction)popupLoadRecentMenu:(id)sender;
- (IBAction)removeSelectedDirectory:(id)sender;

- (void)addDirectory:(NSString *)directory;
- (void)refreshRemoveButtonText;
@end
