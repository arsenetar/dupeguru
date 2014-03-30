#import <Cocoa/Cocoa.h>

@interface CocoaProxy : NSObject
{
	NSAutoreleasePool *currentPool;
}
- (void)openPath:(NSString *)path;
- (void)openURL:(NSString *)url;
- (void)revealPath:(NSString *)path;
- (NSString *)getUTI:(NSString *)path;
- (BOOL)type:(NSString *)type conformsToType:(NSString *)refType;
- (NSString *)getAppdataPath; 
- (NSString *)getCachePath;
- (NSString *)getResourcePath;
- (NSString *)systemLang;
- (NSString *)systemShortDateFormat;
- (NSString *)systemNumberDecimalSeparator;
- (NSString *)systemNumberGroupingSeparator;
- (NSString *)systemCurrency;
- (NSString *)bundleIdentifier;
- (NSString *)appVersion;
- (NSString *)osxVersion;
- (NSString *)bundleInfo:(NSString *)key;
- (void)postNotification:(NSString *)name userInfo:(NSDictionary *)userInfo;
- (id)prefValue:(NSString *)prefname;
- (void)setPrefValue:(NSString *)prefname value:(id)value;
- (id)prefValue:(NSString *)prefname inDomain:(NSString *)domain;
- (NSString *)url2path:(NSString *)url;
- (void)createPool;
- (void)destroyPool;
- (void)reportCrash:(NSString *)crashReport withGithubUrl:(NSString *)githubUrl;
- (void)log:(NSString *)s;
- (NSDictionary *)readExifData:(NSString *)imagePath;
@end