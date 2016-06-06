/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import <Sparkle/SUUpdater.h>
#import "PyDupeGuru.h"
#import "ResultWindow.h"
#import "ResultTable.h"
#import "DetailsPanel.h"
#import "DirectoryPanel.h"
#import "IgnoreListDialog.h"
#import "ProblemDialog.h"
#import "DeletionOptions.h"
#import "HSAboutBox.h"
#import "HSRecentFiles.h"
#import "HSProgressWindow.h"

@interface AppDelegate : NSObject <NSFileManagerDelegate>
{
    NSMenu *recentResultsMenu;
    NSMenu *columnsMenu;
    SUUpdater *updater;
    
    PyDupeGuru *model;
    ResultWindow *_resultWindow;
    DirectoryPanel *_directoryPanel;
    DetailsPanel *_detailsPanel;
    IgnoreListDialog *_ignoreListDialog;
    ProblemDialog *_problemDialog;
    DeletionOptions *_deletionOptions;
    HSProgressWindow *_progressWindow;
    NSWindowController *_preferencesPanel;
    HSAboutBox *_aboutBox;
    HSRecentFiles *_recentResults;
}

@property (readwrite, retain) NSMenu *recentResultsMenu;
@property (readwrite, retain) NSMenu *columnsMenu;
@property (readwrite, retain) SUUpdater *updater;

/* Virtual */
+ (NSDictionary *)defaultPreferences;
- (PyDupeGuru *)model;
- (DetailsPanel *)createDetailsPanel;
- (void)setScanOptions;

/* Public */
- (void)finalizeInit;
- (ResultWindow *)resultWindow;
- (DirectoryPanel *)directoryPanel;
- (DetailsPanel *)detailsPanel;
- (HSRecentFiles *)recentResults;
- (NSInteger)getAppMode;
- (void)setAppMode:(NSInteger)appMode;

/* Delegate */
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification;
- (void)applicationWillBecomeActive:(NSNotification *)aNotification;
- (NSApplicationTerminateReply)applicationShouldTerminate:(NSApplication *)sender;
- (void)applicationWillTerminate:(NSNotification *)aNotification;
- (void)recentFileClicked:(NSString *)path;

/* Actions */
- (void)clearPictureCache;
- (void)loadResults;
- (void)openWebsite;
- (void)openHelp;
- (void)showAboutBox;
- (void)showDirectoryWindow;
- (void)showPreferencesPanel;
- (void)showResultWindow;
- (void)showIgnoreList;
- (void)startScanning;

/* model --> view */
- (void)showMessage:(NSString *)msg;
@end
