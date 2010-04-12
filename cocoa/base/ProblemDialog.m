/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "ProblemDialog.h"
#import "Utils.h"

@implementation ProblemDialog
- (id)initWithPy:(PyApp *)aPy
{
    self = [super initWithNibName:@"ProblemDialog" pyClassName:@"PyProblemDialog" pyParent:aPy];
    [self window]; //So the detailsTable is initialized.
    problemTable = [[HSTable alloc] initWithPyClassName:@"PyProblemTable" pyParent:[self py] view:problemTableView];
    [self connect];
    [problemTable connect];
    return self;
}

- (void)dealloc
{
    [problemTable disconnect];
    [self disconnect];
    [problemTable release];
    [super dealloc];
}

- (PyProblemDialog *)py
{
    return (PyProblemDialog *)py;
}

- (IBAction)revealSelected:(id)sender
{
    [[self py] revealSelected];
}
@end