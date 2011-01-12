/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "RecentDirectories.h"
#import "PyDupeGuru.h"
#import "ResultWindow.h"
#import "DetailsPanel.h"
#import "DirectoryPanel.h"
#import "HSAboutBox.h"

@interface AppDelegateBase : NSObject
{
    IBOutlet PyDupeGuruBase *py;
    IBOutlet RecentDirectories *recentDirectories;
    IBOutlet ResultWindowBase *result;
    
    DirectoryPanel *_directoryPanel;
    DetailsPanel *_detailsPanel;
    HSAboutBox *_aboutBox;
    BOOL _savedResults;
}
- (PyDupeGuruBase *)py;
- (RecentDirectories *)recentDirectories;
- (DirectoryPanel *)directoryPanel;
- (DetailsPanel *)detailsPanel;
- (void)saveResults;

- (IBAction)showAboutBox:(id)sender;
- (IBAction)openWebsite:(id)sender;
- (IBAction)openHelp:(id)sender;
@end
