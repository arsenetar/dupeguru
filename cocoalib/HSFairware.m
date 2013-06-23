/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "HSFairware.h"
#import <CommonCrypto/CommonDigest.h>
#import "HSFairwareReminder.h"
#import "Dialogs.h"
#import "Utils.h"

NSString* md5str(NSString *source)
{
    const char *cSource = [source UTF8String];
    unsigned char result[16];
    CC_MD5(cSource, strlen(cSource), result);
    return fmt(@"%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x",
        result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7],
        result[8], result[9], result[10], result[11], result[12], result[13], result[14], result[15]
    );
}

BOOL validateCode(NSString *code, NSString *email, NSInteger appId)
{
    if ([code length] != 32) {
        return NO;
    }
    NSInteger i;
    for (i=0; i<=100; i++) {
        NSString *blob = fmt(@"%i%@%iaybabtu", appId, email, i);
        if ([md5str(blob) isEqualTo:code]) {
            return YES;
        }
    }
    return NO;
}

NSString* normalizeString(NSString *str)
{
    return [[str stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]] lowercaseString];
}

@implementation HSFairware
- (id)initWithAppId:(NSInteger)aAppId name:(NSString *)aName;
{
    self = [super init];
    appId = aAppId;
    name = [aName retain];
    registered = NO;
    return self;
}

- (void)dealloc
{
    [name release];
    [super dealloc];
}

/* Private */
- (void)setRegistrationCode:(NSString *)aCode email:(NSString *)aEmail
{
    registered = validateCode(aCode, aEmail, appId);
}

/* Public */
- (void)initialRegistrationSetup
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSString *code = [ud stringForKey:@"RegistrationCode"];
    NSString *email = [ud stringForKey:@"RegistrationEmail"];
    if (code && email) {
        [self setRegistrationCode:code email:email];
    }
    if (!registered) {
        BOOL fairwareMode = [ud boolForKey:@"FairwareMode"];
        if (!fairwareMode) {
            NSString *prompt = @"%@ is fairware, which means \"open source software developed "
                "with expectation of fair contributions from users\". It's a very interesting "
                "concept, but one year of fairware has shown that most people just want to know "
                "how much it costs and not be bothered with theories about intellectual property."
                "\n\n"
                "So I won't bother you and will be very straightforward: You can try %@ for "
                "free but you have to buy it in order to use it without limitations. In demo mode, "
                "%@ will show this dialog on startup."
                "\n\n"
                "So it's as simple as this. If you're curious about fairware, however, I encourage "
                "you to read more about it by clicking on the \"Fairware?\" button.";
            [HSFairwareReminder showDemoNagWithApp:self prompt:fmt(prompt, name, name, name)];
        }
    }
}

- (NSString *)appName
{
    return name;
}

- (NSString *)appLongName
{
    return name;
}

- (BOOL)isRegistered
{
    return registered;
}

- (BOOL)setRegisteredCode:(NSString *)code andEmail:(NSString *)email
{
    code = normalizeString(code);
    email = normalizeString(email);
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    if (([code isEqualTo:@"fairware"]) || ([email isEqualTo:@"fairware"])) {
        [ud setBool:YES forKey:@"FairwareMode"];
        [Dialogs showMessage:@"Fairware mode enabled."];
        return YES;
    }
    [self setRegistrationCode:code email:email];
    if (registered) {
        [ud setObject:code forKey:@"RegistrationCode"];
        [ud setObject:email forKey:@"RegistrationEmail"];
        [Dialogs showMessage:@"Your code is valid, thanks!"];
        return YES;
    }
    else {
        [Dialogs showMessage:@"Your code is invalid. Make sure that you wrote the good code. Also "
            "make sure that the e-mail you gave is the same as the e-mail you used for your purchase."];
        return NO;
    }
}

- (void)contribute
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://open.hardcoded.net/contribute/"]];
}

- (void)buy
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://www.hardcoded.net/purchase.htm"]];
}

- (void)aboutFairware
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://open.hardcoded.net/about/"]];
}

@end