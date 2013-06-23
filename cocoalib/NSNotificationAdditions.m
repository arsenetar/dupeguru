#import "NSNotificationAdditions.h"
#import <pthread.h>

@implementation NSNotificationCenter (NSNotificationCenterAdditions)
- (void) postNotificationOnMainThread:(NSNotification *) notification {
	if( pthread_main_np() ) return [self postNotification:notification];
	[self postNotificationOnMainThread:notification waitUntilDone:NO];
}

- (void) postNotificationOnMainThread:(NSNotification *) notification waitUntilDone:(BOOL) wait {
	if( pthread_main_np() ) return [self postNotification:notification];
	[[self class] performSelectorOnMainThread:@selector( _postNotification: ) withObject:notification waitUntilDone:wait];
}

+ (void) _postNotification:(NSNotification *) notification {
	[[self defaultCenter] postNotification:notification];
}

- (void) postNotificationOnMainThreadWithName:(NSString *) name object:(id) object {
	if( pthread_main_np() ) return [self postNotificationName:name object:object userInfo:nil];
	[self postNotificationOnMainThreadWithName:name object:object userInfo:nil waitUntilDone:NO];
}

- (void) postNotificationOnMainThreadWithName:(NSString *) name object:(id) object userInfo:(NSDictionary *) userInfo {
	if( pthread_main_np() ) return [self postNotificationName:name object:object userInfo:userInfo];
	[self postNotificationOnMainThreadWithName:name object:object userInfo:nil waitUntilDone:NO];
}

- (void) postNotificationOnMainThreadWithName:(NSString *) name object:(id) object userInfo:(NSDictionary *) userInfo waitUntilDone:(BOOL) wait {
	if( pthread_main_np() ) return [self postNotificationName:name object:object userInfo:userInfo];

	NSMutableDictionary *info = [[NSMutableDictionary allocWithZone:nil] init];
	[info setObject:name forKey:@"name"];
	if( object ) [info setObject:object forKey:@"object"];
	if( userInfo ) [info setObject:userInfo forKey:@"userInfo"];

	[[self class] performSelectorOnMainThread:@selector( _postNotificationName: ) withObject:info waitUntilDone:wait];
	[info release];
}

+ (void) _postNotificationName:(NSDictionary *) info {
	NSString *name = [info objectForKey:@"name"];
	id object = [info objectForKey:@"object"];
	NSDictionary *userInfo = [info objectForKey:@"userInfo"];

	[[self defaultCenter] postNotificationName:name object:object userInfo:userInfo];
}
@end