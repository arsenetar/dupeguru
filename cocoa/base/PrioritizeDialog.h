/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyPrioritizeDialog.h"
#import "HSPopUpList.h"
#import "HSSelectableList.h"
#import "PrioritizeList.h"

@interface PrioritizeDialog : NSWindowController
{
    IBOutlet NSPopUpButton *categoryPopUpView;
    IBOutlet NSTableView *criteriaTableView;
    IBOutlet NSTableView *prioritizationTableView;
    
    PyPrioritizeDialog *model;
    HSPopUpList *categoryPopUp;
    HSSelectableList *criteriaList;
    PrioritizeList *prioritizationList;
}
- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyPrioritizeDialog *)model;

- (IBAction)addSelected:(id)sender;
- (IBAction)removeSelected:(id)sender;
- (IBAction)ok:(id)sender;
- (IBAction)cancel:(id)sender;
@end;