/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "RecentDirectories.h"
#import "Outline.h"
#import "PyDupeGuru.h"

@interface DirectoryOutline : OutlineView
{
}
@end

@protocol DirectoryOutlineDelegate
- (void)outlineView:(NSOutlineView *)outlineView addDirectory:(NSString *)directory;
@end

@interface DirectoryPanel : NSWindowController
{
    IBOutlet NSPopUpButton *addButtonPopUp;
    IBOutlet DirectoryOutline *directories;
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
