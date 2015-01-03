/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import "PyBaseApp.h"

@interface HSAboutBox : NSWindowController
{
    NSTextField *titleTextField;
    NSTextField *versionTextField;
    NSTextField *copyrightTextField;
    
    PyBaseApp *app;
}

@property (readwrite, retain) NSTextField *titleTextField;
@property (readwrite, retain) NSTextField *versionTextField;
@property (readwrite, retain) NSTextField *copyrightTextField;

- (id)initWithApp:(PyBaseApp *)app;
- (void)updateFields;
@end