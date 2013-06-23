/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyFairware.h"

@interface HSFairwareAboutBox : NSWindowController
{
    NSTextField *titleTextField;
    NSTextField *versionTextField;
    NSTextField *copyrightTextField;
    NSTextField *registeredTextField;
    NSButton *registerButton;
    
    PyFairware *app;
}

@property (readwrite, retain) NSTextField *titleTextField;
@property (readwrite, retain) NSTextField *versionTextField;
@property (readwrite, retain) NSTextField *copyrightTextField;
@property (readwrite, retain) NSTextField *registeredTextField;
@property (readwrite, retain) NSButton *registerButton;

- (id)initWithApp:(PyFairware *)app;
- (void)updateFields;

- (void)showRegisterDialog;
@end