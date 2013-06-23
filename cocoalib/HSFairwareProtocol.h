/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>

@protocol HSFairwareProtocol
- (void)initialRegistrationSetup;
- (NSString *)appName;
- (NSString *)appLongName;
- (BOOL)isRegistered;
- (BOOL)setRegisteredCode:(NSString *)code andEmail:(NSString *)email;
- (void)contribute;
- (void)buy;
- (void)aboutFairware;
@end