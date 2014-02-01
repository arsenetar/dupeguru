/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "HSQuicklook.h"

@implementation HSQLPreviewItem
- (id)initWithUrl:(NSURL *)aUrl title:(NSString *)aTitle
{
    self = [super init];
    url = [aUrl retain];
    title = [aTitle retain];
    return self;
}

- (void)dealloc
{
    [url release];
    [title release];
    [super dealloc];
}

- (NSURL *)previewItemURL
{
    return url;
}

- (NSString *)previewItemTitle
{
    return title;
}
@end