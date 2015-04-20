/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import "Worker.h"

extern NSString *JobCompletedNotification;
extern NSString *JobCancelledNotification;

@interface ProgressController : NSWindowController <NSWindowDelegate>
{
    NSButton *cancelButton;
    NSProgressIndicator *progressBar;
    NSTextField *statusText;
    NSTextField *descText;
    
    id _jobId;
    BOOL _running;
    NSObject<Worker> *_worker;
}

@property (readwrite, retain) NSButton *cancelButton;
@property (readwrite, retain) NSProgressIndicator *progressBar;
@property (readwrite, retain) NSTextField *statusText;
@property (readwrite, retain) NSTextField *descText;

+ (ProgressController *)mainProgressController;

- (id)init;

- (void)cancel;

- (void)hide;
- (void)show;
- (void)showWithCancelButton:(BOOL)cancelEnabled;
- (void)showSheetForParent:(NSWindow *) parentWindow;
- (void)showSheetForParent:(NSWindow *) parentWindow withCancelButton:(BOOL)cancelEnabled;

/* Properties */
- (BOOL)isShown;
- (id)jobId;
- (void)setJobId:(id)jobId;
- (void)setJobDesc:(NSString *)desc;
- (void)setWorker:(NSObject<Worker> *)worker;
@end
