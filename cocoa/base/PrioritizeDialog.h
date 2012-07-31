/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyPrioritizeDialog.h"
#import "HSPopUpList.h"
#import "HSSelectableList.h"
#import "PrioritizeList.h"
#import "PyDupeGuru.h"

@interface PrioritizeDialog : NSWindowController
{
    NSPopUpButton *categoryPopUpView;
    NSTableView *criteriaTableView;
    NSTableView *prioritizationTableView;
    
    PyPrioritizeDialog *model;
    HSPopUpList *categoryPopUp;
    HSSelectableList *criteriaList;
    PrioritizeList *prioritizationList;
}

@property (readwrite, retain) NSPopUpButton *categoryPopUpView;
@property (readwrite, retain) NSTableView *criteriaTableView;
@property (readwrite, retain) NSTableView *prioritizationTableView;

- (id)initWithApp:(PyDupeGuru *)aApp;
- (PyPrioritizeDialog *)model;

- (void)ok;
- (void)cancel;
@end;