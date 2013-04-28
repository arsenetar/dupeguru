/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "Utils.h"
#import "ValueTransformers.h"
#import "Consts.h"
#import "DetailsPanel.h"
#import "DirectoryPanel.h"
#import "ResultWindow.h"

@implementation AppDelegate
+ (NSDictionary *)defaultPreferences
{
    NSMutableDictionary *d = [NSMutableDictionary dictionaryWithDictionary:[super defaultPreferences]];
    [d setObject:i2n(0) forKey:@"scanType"];
    [d setObject:i2n(95) forKey:@"minMatchPercentage"];
    [d setObject:b2n(NO) forKey:@"matchScaled"];
    return d;
}

- (id)init
{
    self = [super init];
    NSMutableIndexSet *i = [NSMutableIndexSet indexSetWithIndex:0];
    VTIsIntIn *vtScanTypeIsFuzzy = [[[VTIsIntIn alloc] initWithValues:i reverse:NO] autorelease];
    [NSValueTransformer setValueTransformer:vtScanTypeIsFuzzy forName:@"vtScanTypeIsFuzzy"];
    return self;
}

- (NSString *)homepageURL
{
    return @"http://www.hardcoded.net/dupeguru_pe/";
}

- (ResultWindowBase *)createResultWindow
{
    return [[ResultWindow alloc] initWithParentApp:self];
}

- (DirectoryPanel *)createDirectoryPanel
{
    return [[DirectoryPanelPE alloc] initWithParentApp:self];
}

- (DetailsPanel *)createDetailsPanel
{
    return [[DetailsPanel alloc] initWithApp:model];
}

- (void)clearPictureCache
{
    [(ResultWindow *)[self resultWindow] clearPictureCache];
}
@end
