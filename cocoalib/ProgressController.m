/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "ProgressController.h"
#import "Utils.h"
#import "ProgressController_UI.h"

NSString *JobCompletedNotification = @"JobCompletedNotification";
NSString *JobCancelledNotification = @"JobCancelledNotification";
static ProgressController *_mainPC = nil;

@implementation ProgressController

@synthesize cancelButton;
@synthesize progressBar;
@synthesize statusText;
@synthesize descText;

+ (ProgressController *)mainProgressController
{
    if (_mainPC == nil)
        _mainPC = [[ProgressController alloc] init];
    return _mainPC;
}

- (id)init
{
    self = [super initWithWindow:nil];
    [self setWindow:createProgressController_UI(self)];
    [progressBar setUsesThreadedAnimation:YES];
    _worker = nil;
    _running = NO;
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(applicationDidBecomeActive:) name:NSApplicationDidBecomeActiveNotification object:nil];
    return self;
}

- (void)cancel
{
    [self hide];
}

- (void)hide
{
    if (_worker != nil)
        [_worker cancelJob];
    [[NSNotificationCenter defaultCenter] postNotificationName:JobCancelledNotification object:self];
    _running = NO;
    [NSApp endSheet:[self window] returnCode:NSRunAbortedResponse];
    /* There's this really strange thing where when the app is inactive at the point we want to hide
       the progress dialog, it becomes impossible to close it. I guess it's due to some strange
       thread-related crap. Anyway, *DO NOT HIDE THE SHEET WHILE THE APP IS INACTIVE*. Do it later,
       when the app becomes active again.
     */
    if ([NSApp isActive]) {
        [[self window] orderOut:nil];
    }
}

- (void)show
{
    [self showWithCancelButton:YES];
}

- (void)showWithCancelButton:(BOOL)cancelEnabled
{
    [progressBar setIndeterminate:YES];
    [[self window] makeKeyAndOrderFront:nil];
    [progressBar setUsesThreadedAnimation:YES];
    [progressBar startAnimation:nil];
    [cancelButton setEnabled:cancelEnabled];
    _running = YES;
    [NSThread detachNewThreadSelector:@selector(threadedWorkerProbe) toTarget:self withObject:nil];
}

- (void)showSheetForParent:(NSWindow *) parentWindow
{
    [self showSheetForParent:parentWindow withCancelButton:YES];
}

- (void)showSheetForParent:(NSWindow *) parentWindow withCancelButton:(BOOL)cancelEnabled
{
    [progressBar setIndeterminate:YES];
    [progressBar startAnimation:nil];
    [cancelButton setEnabled:cancelEnabled];
    _running = YES;
    [NSThread detachNewThreadSelector:@selector(threadedWorkerProbe) toTarget:self withObject:nil];
    [NSApp beginSheet:[self window] modalForWindow:parentWindow modalDelegate:nil didEndSelector:nil contextInfo:nil];
}

- (void)updateProgress
{
    if (!_running)
        return;
    NSNumber *progress = [_worker getJobProgress];
    NSString *status = [_worker getJobDesc];
    if ((status != nil) && ([status length] > 0))
    {
        [statusText setStringValue:status];
    }
    if (progress != nil)
    {
        [progressBar setDoubleValue:n2i(progress)];
        [progressBar setIndeterminate: n2i(progress) < 0];
    }
    else
    {
        [self hide];
        [_worker jobCompleted:_jobId];
        [[NSNotificationCenter defaultCenter] postNotificationName:JobCompletedNotification object:self];
    }
}

- (void)threadedWorkerProbe
{
    while (_running && (_worker != nil))
    {
        NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
        [NSThread sleepUntilDate:[NSDate dateWithTimeIntervalSinceNow:1]];
        [self performSelectorOnMainThread:@selector(updateProgress) withObject:nil waitUntilDone:YES];
        [pool release];
    }
}

/* Properties */
- (BOOL)isShown
{
    return _running;
}

- (id)jobId {return _jobId;}
- (void)setJobId:(id)jobId
{
    [_jobId autorelease];
    _jobId = [jobId retain];
}

- (void)setJobDesc:(NSString *)desc
{
    [descText setStringValue:desc];
    [statusText setStringValue:NSLocalizedStringFromTable(@"Please wait...", @"cocoalib", @"")];
}

- (void)setWorker:(NSObject<Worker> *)worker
{
    _worker = worker;
}

/* Delegate and Notifs */
- (void)applicationDidBecomeActive:(NSNotification *)notification
{
    if (!_running) {
        [[self window] orderOut:nil];
    }
}
@end
