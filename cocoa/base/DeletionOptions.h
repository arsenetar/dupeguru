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
    
    PyDeletionOptions *model;
    
    NSTextField *messageTextField;
    NSButton *linkButton;
    NSMatrix *linkTypeRadio;
    NSButton *directButton;
}

@property (readwrite, retain) NSTextField *messageTextField;
@property (readwrite, retain) NSButton *linkButton;
@property (readwrite, retain) NSMatrix *linkTypeRadio;
@property (readwrite, retain) NSButton *directButton;

- (id)initWithPyRef:(PyObject *)aPyRef;

- (void)updateOptions;
- (void)proceed;
- (void)cancel;
@end