/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyDupeGuru.h"
#import "ResultWindow.h"
#import "DetailsPanel.h"
#import "DirectoryPanel.h"
#import "HSAboutBox.h"
#import "HSRecentFiles.h"

@interface AppDelegateBase : NSObject
{
    IBOutlet PyDupeGuruBase *py;
    IBOutlet NSMenu *recentResultsMenu;
    IBOutlet NSMenu *columnsMenu;
    
    ResultWindowBase *_resultWindow;
    DirectoryPanel *_directoryPanel;
    DetailsPanel *_detailsPanel;
    HSAboutBox *_aboutBox;
    HSRecentFiles *_recentResults;
}

/* Virtual */
- (PyDupeGuruBase *)py;
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

/* Actions */
- (IBAction)showAboutBox:(id)sender;
- (IBAction)openWebsite:(id)sender;
- (IBAction)openHelp:(id)sender;
- (IBAction)toggleDirectories:(id)sender;
@end
