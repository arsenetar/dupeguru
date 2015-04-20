/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import "HSOutlineView.h"
#import "HSRecentFiles.h"
#import "DirectoryOutline.h"
#import "PyDupeGuru.h"

@class AppDelegateBase;

@interface DirectoryPanel : NSWindowController <NSOpenSavePanelDelegate>
{
    AppDelegateBase *_app;
    PyDupeGuru *model;
    HSRecentFiles *_recentDirectories;
    DirectoryOutline *outline;
    BOOL _alwaysShowPopUp;
    NSPopUpButton *addButtonPopUp;
    NSPopUpButton *loadRecentButtonPopUp;
    HSOutlineView *outlineView;
    NSButton *removeButton;
    NSButton *loadResultsButton;
}

@property (readwrite, retain) NSPopUpButton *addButtonPopUp;
@property (readwrite, retain) NSPopUpButton *loadRecentButtonPopUp;
@property (readwrite, retain) HSOutlineView *outlineView;
@property (readwrite, retain) NSButton *removeButton;
@property (readwrite, retain) NSButton *loadResultsButton;

- (id)initWithParentApp:(AppDelegateBase *)aParentApp;

- (void)fillPopUpMenu; // Virtual
- (void)adjustUIToLocalization;

- (void)askForDirectory;
- (void)popupAddDirectoryMenu:(id)sender;
- (void)popupLoadRecentMenu:(id)sender;
- (void)removeSelectedDirectory;

- (void)addDirectory:(NSString *)directory;
- (void)refreshRemoveButtonText;
- (void)markAll;

@end
