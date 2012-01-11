#import <Cocoa/Cocoa.h>

@protocol ExtraFairwareReminderView <NSObject>
- (void)startTimer;
- (void)stopTimer;
- (void)setButtonText:(NSString *)text;
- (void)enableButton;
@end