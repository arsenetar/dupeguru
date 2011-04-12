/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSWindowController.h"
#import "PyApp.h"
#import "PyDetailsPanel.h"

@interface DetailsPanel : HSWindowController
{
    IBOutlet NSTableView *detailsTable;
}
- (id)initWithPy:(PyApp *)aPy;
- (PyDetailsPanel *)py;

- (BOOL)isVisible;
- (void)toggleVisibility;

/* Python --> Cocoa */
- (void)refresh;
@end