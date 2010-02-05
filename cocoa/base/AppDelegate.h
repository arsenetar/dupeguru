/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "RecentDirectories.h"
#import "PyDupeGuru.h"
#import "ResultWindow.h"
#import "DetailsPanel.h"
#import "DirectoryPanel.h"

@interface AppDelegateBase : NSObject
{
    IBOutlet PyDupeGuruBase *py;
    IBOutlet RecentDirectories *recentDirectories;
    IBOutlet NSMenuItem *unlockMenuItem;
    IBOutlet ResultWindowBase *result;
    
    DirectoryPanel *_directoryPanel;
    DetailsPanel *_detailsPanel;
    BOOL _savedResults;
}
- (IBAction)unlockApp:(id)sender;

- (PyDupeGuruBase *)py;
- (RecentDirectories *)recentDirectories;
- (DirectoryPanel *)directoryPanel;
- (DetailsPanel *)detailsPanel;
- (void)saveResults;
@end
