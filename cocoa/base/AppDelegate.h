/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyDupeGuru.h"
#import "ResultWindow.h"
#import "DetailsPanel.h"
#import "DirectoryPanel.h"
#import "IgnoreListDialog.h"
#import "HSAboutBox.h"
#import "HSRecentFiles.h"

@interface AppDelegateBase : NSObject
{
    IBOutlet NSMenu *recentResultsMenu;
    IBOutlet NSMenu *actionsMenu;
    IBOutlet NSMenu *columnsMenu;
    
    PyDupeGuru *model;
    ResultWindowBase *_resultWindow;
    DirectoryPanel *_directoryPanel;
    DetailsPanel *_detailsPanel;
    IgnoreListDialog *_ignoreListDialog;
    NSWindowController *_preferencesPanel;
    HSAboutBox *_aboutBox;
    HSRecentFiles *_recentResults;
}

/* Virtual */
- (PyDupeGuru *)model;
- (ResultWindowBase *)createResultWindow;
- (DirectoryPanel *)createDirectoryPanel;
- (DetailsPanel *)createDetailsPanel;
- (NSString *)homepageURL;

/* Public */
- (ResultWindowBase *)resultWindow;
- (DirectoryPanel *)directoryPanel;
- (DetailsPanel *)detailsPanel;
- (HSRecentFiles *)recentResults;
- (NSMenu *)columnsMenu;

/* Delegate */
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification;
- (void)applicationWillBecomeActive:(NSNotification *)aNotification;
- (NSApplicationTerminateReply)applicationShouldTerminate:(NSApplication *)sender;
- (void)applicationWillTerminate:(NSNotification *)aNotification;
- (void)recentFileClicked:(NSString *)path;

/* Actions */
- (IBAction)loadResults:(id)sender;
- (IBAction)openWebsite:(id)sender;
- (IBAction)openHelp:(id)sender;
- (IBAction)showAboutBox:(id)sender;
- (IBAction)showDirectoryWindow:(id)sender;
- (IBAction)showPreferencesPanel:(id)sender;
- (IBAction)showResultWindow:(id)sender;
- (IBAction)showIgnoreList:(id)sender;
- (IBAction)startScanning:(id)sender;

/* model --> view */
- (void)showMessage:(NSString *)msg;
- (void)setupAsRegistered;
- (void)showFairwareNagWithPrompt:(NSString *)prompt;
- (void)showDemoNagWithPrompt:(NSString *)prompt;
@end
