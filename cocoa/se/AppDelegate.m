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
#import "DetailsPanel.h"
#import "DirectoryPanel.h"
#import "ResultWindow.h"
#import "Consts.h"

@implementation AppDelegate
+ (void)initialize
{
    [super initialize];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSMutableDictionary *d = [NSMutableDictionary dictionary];
    [d setObject:i2n(1) forKey:@"scanType"];
    [d setObject:i2n(80) forKey:@"minMatchPercentage"];
    [d setObject:i2n(30) forKey:@"smallFileThreshold"];
    [d setObject:i2n(1) forKey:@"recreatePathType"];
    [d setObject:i2n(11) forKey:TableFontSize];
    [d setObject:b2n(YES) forKey:@"wordWeighting"];
    [d setObject:b2n(NO) forKey:@"matchSimilarWords"];
    [d setObject:b2n(YES) forKey:@"mixFileKind"];
    [d setObject:b2n(NO) forKey:@"useRegexpFilter"];
    [d setObject:b2n(NO) forKey:@"ignoreHardlinkMatches"];
    [d setObject:b2n(NO) forKey:@"removeEmptyFolders"];
    [d setObject:b2n(YES) forKey:@"ignoreSmallFiles"];
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
    NSMutableIndexSet *contentsIndexes = [NSMutableIndexSet indexSet];
    [contentsIndexes addIndex:1];
    [contentsIndexes addIndex:2];
    VTIsIntIn *vt = [[[VTIsIntIn alloc] initWithValues:contentsIndexes reverse:YES] autorelease];
    [NSValueTransformer setValueTransformer:vt forName:@"vtScanTypeIsNotContent"];
    _directoryPanel = nil;
    return self;
}

- (NSString *)homepageURL
{
    return @"http://www.hardcoded.net/dupeguru/";
}

- (ResultWindowBase *)createResultWindow
{
    return [[ResultWindow alloc] initWithParentApp:self];
}
@end
