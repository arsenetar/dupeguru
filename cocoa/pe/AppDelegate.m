/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

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
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSMutableDictionary *d = [NSMutableDictionary dictionaryWithCapacity:10];
    [d setObject:[NSNumber numberWithInt:95] forKey:@"minMatchPercentage"];
    [d setObject:[NSNumber numberWithInt:1] forKey:@"recreatePathType"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"matchScaled"];
    [d setObject:[NSNumber numberWithBool:YES] forKey:@"mixFileKind"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"useRegexpFilter"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"ignoreHardlinkMatches"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"removeEmptyFolders"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"debug"];
    [d setObject:[NSArray array] forKey:@"recentDirectories"];
    [d setObject:[NSArray array] forKey:@"columnsOrder"];
    [d setObject:[NSDictionary dictionary] forKey:@"columnsWidth"];
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [ud registerDefaults:d];
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
    return [[DetailsPanelPE alloc] initWithPy:py];
}

- (PyDupeGuru *)py { return (PyDupeGuru *)py; }

//Delegate
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    // index 2 is just after "Clear Ingore List"
    NSMenuItem *mi = [actionsMenu insertItemWithTitle:TR(@"Clear Picture Cache")
        action:@selector(clearPictureCache:) keyEquivalent:@"P" atIndex:2];
    [mi setTarget:[self resultWindow]];
    [mi setKeyEquivalentModifierMask:NSCommandKeyMask|NSShiftKeyMask];
    [super applicationDidFinishLaunching:aNotification];
}
@end
