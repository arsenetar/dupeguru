/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyApp.h"
#import "PyPrioritizeDialog.h"
#import "HSPopUpList2.h"
#import "HSSelectableList2.h"
#import "PrioritizeList.h"

@interface PrioritizeDialog : NSWindowController
{
    IBOutlet NSPopUpButton *categoryPopUpView;
    IBOutlet NSTableView *criteriaTableView;
    IBOutlet NSTableView *prioritizationTableView;
    
    PyPrioritizeDialog *py;
    HSPopUpList2 *categoryPopUp;
    HSSelectableList2 *criteriaList;
    PrioritizeList *prioritizationList;
}
- (id)init;
- (PyPrioritizeDialog *)py;

- (IBAction)addSelected:(id)sender;
- (IBAction)removeSelected:(id)sender;
- (IBAction)ok:(id)sender;
- (IBAction)cancel:(id)sender;
@end;