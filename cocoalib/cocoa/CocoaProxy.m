#import "CocoaProxy.h"
#import "HSErrorReportWindow.h"

@implementation CocoaProxy
- (void)openPath:(NSString *)path
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL fileURLWithPath:path isDirectory:NO]];
}

- (void)openURL:(NSString *)url
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:url]];
}

- (void)revealPath:(NSString *)path
{
    [[NSWorkspace sharedWorkspace] selectFile:path inFileViewerRootedAtPath:@""];
}

- (NSString *)getUTI:(NSString *)path
{
    NSError *error;
    return [[NSWorkspace sharedWorkspace] typeOfFile:path error:&error];
}

- (BOOL)type:(NSString *)type conformsToType:(NSString *)refType
{
    return [[NSWorkspace sharedWorkspace] type:type conformsToType:refType];
}

- (NSString *)getAppdataPath
{
    return [NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, YES) objectAtIndex:0];
}
- (NSString *)getCachePath
{
    return [NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES) objectAtIndex:0];
}

- (NSString *)getResourcePath
{
    return [[[NSBundle mainBundle] resourceURL] path];
}

- (NSString *)systemLang
{
    return [[NSBundle preferredLocalizationsFromArray:[[NSBundle mainBundle] localizations]] objectAtIndex:0];
}

- (NSString *)systemShortDateFormat
{
    [NSDateFormatter setDefaultFormatterBehavior:NSDateFormatterBehavior10_4];
    NSDateFormatter *f = [[NSDateFormatter alloc] init];
    [f setDateStyle:NSDateFormatterShortStyle];
    [f setTimeStyle:NSDateFormatterNoStyle];
    NSString *result = [[f dateFormat] retain];
    [f release];
    return [result autorelease];
}

- (NSString *)systemNumberDecimalSeparator
{
    [NSNumberFormatter setDefaultFormatterBehavior:NSNumberFormatterBehavior10_4];
    NSNumberFormatter *f = [[NSNumberFormatter alloc] init];
    NSString *result = [[f decimalSeparator] retain];
    [f release];
    return [result autorelease];
}

- (NSString *)systemNumberGroupingSeparator
{
    [NSNumberFormatter setDefaultFormatterBehavior:NSNumberFormatterBehavior10_4];
    NSNumberFormatter *f = [[NSNumberFormatter alloc] init];
    NSString *result = [[f groupingSeparator] retain];
    [f release];
    return [result autorelease];
}

- (NSString *)systemCurrency
{
    return [[NSLocale currentLocale] objectForKey:NSLocaleCurrencyCode];
}

- (NSString *)bundleIdentifier
{
    return [[NSBundle mainBundle] bundleIdentifier];
}

- (NSString *)appVersion
{
    return [[NSBundle mainBundle] objectForInfoDictionaryKey:@"CFBundleVersion"];
}

- (NSString *)bundleInfo:(NSString *)key
{
    return [[NSBundle mainBundle] objectForInfoDictionaryKey:key];
}

- (NSString *)osxVersion
{
    return [[NSProcessInfo processInfo] operatingSystemVersionString];
}

- (void)postNotification:(NSString *)name userInfo:(NSDictionary *)userInfo
{
    [[NSNotificationCenter defaultCenter] postNotificationName:name object:nil userInfo:userInfo];
}

- (id)prefValue:(NSString *)prefname
{
    return [[NSUserDefaults standardUserDefaults] objectForKey:prefname];
}

- (void)setPrefValue:(NSString *)prefname value:(id)value
{
    [[NSUserDefaults standardUserDefaults] setObject:value forKey:prefname];
}

- (id)prefValue:(NSString *)prefname inDomain:(NSString *)domain
{
    NSDictionary *dict = [[NSUserDefaults standardUserDefaults] persistentDomainForName:domain];
    return [dict objectForKey:prefname];
}

// Changes a file:/// path into a normal path
- (NSString *)url2path:(NSString *)url
{
    NSURL *u = [NSURL URLWithString:url];
    return [u path];
}

// Create a pool for use into a separate thread.
- (void)createPool
{
    [self destroyPool];
    currentPool = [[NSAutoreleasePool alloc] init];
}
- (void)destroyPool
{
    if (currentPool != nil) {
        [currentPool release];
        currentPool = nil;
    }
}

- (void)reportCrash:(NSString *)crashReport withGithubUrl:(NSString *)githubUrl
{
    return [HSErrorReportWindow showErrorReportWithContent:crashReport githubUrl:githubUrl];
}

- (void)log:(NSString *)s
{
    NSLog(@"%@", s);
}

- (NSDictionary *)readExifData:(NSString *)imagePath
{
    NSDictionary *result = nil;
    NSURL* url = [NSURL fileURLWithPath:imagePath];
    CGImageSourceRef source = CGImageSourceCreateWithURL((CFURLRef)url, nil);
    if (source != nil) {
        CFDictionaryRef metadataRef = CGImageSourceCopyPropertiesAtIndex (source, 0, nil);
        if (metadataRef != nil) {
            result = [NSDictionary dictionaryWithDictionary:(NSDictionary *)metadataRef];
            CFRelease(metadataRef);
        }
        CFRelease(source);
    }
    return result;
}
@end