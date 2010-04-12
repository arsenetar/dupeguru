/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "HSWindowController.h"
#import "PyApp.h"
#import "PyProblemDialog.h"
#import "HSTable.h"

@interface ProblemDialog : HSWindowController
{
    IBOutlet NSTableView *problemTableView;
    
    HSTable *problemTable;
}
- (id)initWithPy:(PyApp *)aPy;
- (PyProblemDialog *)py;

- (IBAction)revealSelected:(id)sender;
@end