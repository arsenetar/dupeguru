/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSRecentFiles.h"

@implementation HSRecentFiles
- (id)initWithName:(NSString *)aName menu:(NSMenu *)aMenu
{
    self = [super init];
    name = aName;
    menu = [aMenu retain];
    numberOfMenuItemsToPreserve = [menu numberOfItems];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    filepaths = [[NSMutableArray alloc] initWithArray:[ud arrayForKey:name]];
    NSFileManager *fm = [NSFileManager defaultManager];
    for (NSInteger i=[filepaths count]-1;i>=0;i--) {
        NSString *path = [filepaths objectAtIndex:i];
        // We check for path class because we might be fed with garbage from the prefs.
        if ((![path isKindOfClass:[NSString class]]) || (![fm fileExistsAtPath:path])) {
            [filepaths removeObjectAtIndex:i];
        }
    }
    [self rebuildMenu];
    return self;
}

- (void)dealloc
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud setObject:filepaths forKey:name];
    [ud synchronize];
    [filepaths release];
    [menu release];
    [super dealloc];
}

- (void)addFile:(NSString *)path
{
    [filepaths removeObject:path];
    [filepaths insertObject:path atIndex:0];
    [self rebuildMenu];
}

- (void)rebuildMenu
{
    while ([menu numberOfItems] > numberOfMenuItemsToPreserve)
        [menu removeItemAtIndex:[menu numberOfItems]-1];
    [self fillMenu:menu];
    if ([filepaths count] > 0) {
        [menu addItem:[NSMenuItem separatorItem]];
        NSMenuItem *mi = [menu addItemWithTitle:NSLocalizedStringFromTable(@"Clear List", @"cocoalib", @"") action:@selector(clearMenu:) keyEquivalent:@""];
        [mi setTarget:self];
    }
}

- (void)fillMenu:(NSMenu *)menuToFill
{
    for (int i=0;i<[filepaths count];i++) {
        NSMenuItem *mi = [menuToFill addItemWithTitle:[filepaths objectAtIndex:i] action:@selector(menuClick:) keyEquivalent:@""];
        [mi setTag:i];
        [mi setTarget:self];
    }
}

- (void)clearMenu:(id)sender
{
    [filepaths removeAllObjects];
    [self rebuildMenu];
}

- (void)menuClick:(id)sender
{
    if (delegate == nil)
        return;
    if ([delegate respondsToSelector:@selector(recentFileClicked:)])
        [delegate recentFileClicked:[filepaths objectAtIndex:[sender tag]]];
}

/* Properties */
- (NSMenu *)menu {return menu;}
- (id)delegate { return delegate; }
- (void)setDelegate:(id)aDelegate { delegate = aDelegate; }
- (NSArray *)filepaths {return filepaths;}
@end
