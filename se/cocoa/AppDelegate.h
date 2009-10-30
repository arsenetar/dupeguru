/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "dgbase/AppDelegate.h"
#import "DirectoryPanel.h"
#import "PyDupeGuru.h"

@interface AppDelegate : AppDelegateBase
{
    DirectoryPanel *_directoryPanel;
}
- (IBAction)openWebsite:(id)sender;
- (IBAction)toggleDirectories:(id)sender;

- (DirectoryPanel *)directoryPanel;
- (PyDupeGuru *)py;
@end
