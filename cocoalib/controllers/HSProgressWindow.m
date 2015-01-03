/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSProgressWindow.h"
#import "ProgressController.h"
#import "Utils.h"

@implementation HSProgressWindow
- (id)initWithPyRef:(PyObject *)aPyRef view:(NSView *)aView
{
    self = [self initWithPyRef:aPyRef wrapperClass:[PyProgressWindow class] callbackClassName:@"ProgressWindowView" view:aView];
    [[ProgressController mainProgressController] setWorker:self];
    jobdescTextField = [[HSTextField alloc] initWithPyRef:[[self model] jobdescTextField] view:[[ProgressController mainProgressController] descText]];
    progressdescTextField = [[HSTextField alloc] initWithPyRef:[[self model] progressdescTextField] view:[[ProgressController mainProgressController] statusText]];
    parentWindow = nil;
    return self;
}

- (PyProgressWindow *)model
{
    return (PyProgressWindow *)model;
}       

/* Public */
- (void)setParentWindow:(NSWindow *)aParentWindow
{
    parentWindow = aParentWindow;
}

- (void)setProgress:(NSInteger)aProgress
{
    progress = aProgress;
}

- (void)showWindow
{
    if (parentWindow != nil) {
        [[ProgressController mainProgressController] showSheetForParent:parentWindow];
    }
    else {
        [[ProgressController mainProgressController] show];
    }
}

- (void)closeWindow
{
    [[ProgressController mainProgressController] hide];
}

/* Worker */

- (NSNumber *)getJobProgress
{
    [[self model] pulse];
    return [NSNumber numberWithInt:progress];
}

- (NSString *)getJobDesc
{
    // Our desc label is updated independently.
    return nil;
}

- (void)cancelJob
{
    [[self model] cancel];
}

- (void)jobCompleted:(NSString *)jobid
{
    // With the new hscommon.gui.progress_window, this call is done from within the core. Do nothing.
}

@end
