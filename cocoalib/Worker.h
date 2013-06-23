#import <Cocoa/Cocoa.h>

//The worker should work in a separate thread or have it's own mechanism to keep the GUI updated as ProgressController
//provides none.
@protocol Worker
// -1: Indeterminate. nil: Not working. 0-100: Progressing
- (NSNumber *)getJobProgress;
- (NSString *)getJobDesc;
- (void)cancelJob;
/* This might seem a little stupid, but it's the simplest way to get a **sync** call to the python
side after a job. Because the python-side app is not an NSObject subclass, it can't listen to
notifications. */
- (void)jobCompleted:(NSString *)jobid;
@end