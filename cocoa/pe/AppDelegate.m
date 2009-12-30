/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "AppDelegate.h"
#import "ProgressController.h"
#import "RegistrationInterface.h"
#import "Utils.h"
#import "ValueTransformers.h"
#import "Consts.h"
#import "DetailsPanel.h"

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
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"removeEmptyFolders"];
    [d setObject:[NSNumber numberWithBool:NO] forKey:@"debug"];
    [d setObject:[NSArray array] forKey:@"recentDirectories"];
    [d setObject:[NSArray array] forKey:@"columnsOrder"];
    [d setObject:[NSDictionary dictionary] forKey:@"columnsWidth"];
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [ud registerDefaults:d];
}

- (id)init
{
    self = [super init];
    _directoryPanel = nil;
    _appName = APPNAME;
    return self;
}

- (DetailsPanelBase *)detailsPanel
{
    if (!_detailsPanel)
        _detailsPanel = [[DetailsPanel alloc] initWithPy:py];
    return _detailsPanel;
}

- (IBAction)openWebsite:(id)sender
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://www.hardcoded.net/dupeguru_pe"]];
}

- (IBAction)toggleDirectories:(id)sender
{
    [[self directoryPanel] toggleVisible:sender];
}

- (DirectoryPanel *)directoryPanel
{
    if (!_directoryPanel)
        _directoryPanel = [[DirectoryPanel alloc] initWithParentApp:self];
    return _directoryPanel;
}
- (PyDupeGuru *)py { return (PyDupeGuru *)py; }

//Delegate
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    NSMenu *actionsMenu = [[[NSApp mainMenu] itemWithTitle:@"Actions"] submenu];
    // index 2 is just after "Clear Ingore List"
    NSMenuItem *mi = [actionsMenu insertItemWithTitle:@"Clear Picture Cache" action:@selector(clearPictureCache:) keyEquivalent:@"P" atIndex:2];
    [mi setTarget:result];
    [mi setKeyEquivalentModifierMask:NSCommandKeyMask|NSShiftKeyMask];
    [super applicationDidFinishLaunching:aNotification];
}

- (void)applicationWillBecomeActive:(NSNotification *)aNotification
{
    if (![[result window] isVisible])
        [result showWindow:NSApp];
}

- (void)applicationWillTerminate:(NSNotification *)aNotification
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud setObject: [result getColumnsOrder] forKey:@"columnsOrder"];
    [ud setObject: [result getColumnsWidth] forKey:@"columnsWidth"];
    [py saveIgnoreList];
    [py saveResults];
    int sc = [ud integerForKey:@"sessionCountSinceLastIgnorePurge"];
    if (sc >= 10)
    {
        sc = -1;
        [py purgeIgnoreList];
    }
    sc++;
    [ud setInteger:sc forKey:@"sessionCountSinceLastIgnorePurge"];
    // NSApplication does not release nib instances objects, we must do it manually
    // Well, it isn't needed because the memory is freed anyway (we are quitting the application
    // But I need to release RecentDirectories so it saves the user defaults
    [recentDirectories release];
}

- (void)recentDirecoryClicked:(NSString *)directory
{
    [[self directoryPanel] addDirectory:directory];
}
@end
