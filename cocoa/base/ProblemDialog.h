/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyProblemDialog.h"
#import "HSTable.h"

@interface ProblemDialog : NSWindowController
{
    IBOutlet NSTableView *problemTableView;
    
    PyProblemDialog *model;
    HSTable *problemTable;
}
- (id)initWithPyRef:(PyObject *)aPyRef;

- (void)initializeColumns;
- (IBAction)revealSelected:(id)sender;
@end