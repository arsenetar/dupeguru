/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

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
+ (void)initialize
{
    [super initialize];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSMutableDictionary *d = [NSMutableDictionary dictionaryWithCapacity:10];
    [d setObject:i2n(0) forKey:@"scanType"];
    [d setObject:i2n(95) forKey:@"minMatchPercentage"];
    [d setObject:i2n(1) forKey:@"recreatePathType"];
    [d setObject:i2n(11) forKey:TableFontSize];
    [d setObject:b2n(NO) forKey:@"matchScaled"];
    [d setObject:b2n(YES) forKey:@"mixFileKind"];
    [d setObject:b2n(NO) forKey:@"useRegexpFilter"];
    [d setObject:b2n(NO) forKey:@"ignoreHardlinkMatches"];
    [d setObject:b2n(NO) forKey:@"removeEmptyFolders"];
    [d setObject:b2n(NO) forKey:@"debug"];
    [d setObject:[NSArray array] forKey:@"recentDirectories"];
    [d setObject:[NSArray array] forKey:@"columnsOrder"];
    [d setObject:[NSDictionary dictionary] forKey:@"columnsWidth"];
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [ud registerDefaults:d];
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
