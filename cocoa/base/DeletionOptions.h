/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyDeletionOptions.h"

@interface DeletionOptions : NSWindowController
{
    IBOutlet NSTextField *messageTextField;
    IBOutlet NSButton *hardlinkButton;
    IBOutlet NSButton *directButton;
    
    PyDeletionOptions *model;
}
- (id)initWithPyRef:(PyObject *)aPyRef;

- (IBAction)updateOptions:(id)sender;
- (IBAction)proceed:(id)sender;
- (IBAction)cancel:(id)sender;
@end