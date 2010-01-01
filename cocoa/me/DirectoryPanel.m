/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "DirectoryPanel.h"

@implementation DirectoryPanel
- (IBAction)addiTunes:(id)sender
{
    [self addDirectory:[@"~/Music/iTunes/iTunes Music" stringByExpandingTildeInPath]];
}

- (IBAction)popupAddDirectoryMenu:(id)sender
{
    NSMenu *m = [addButtonPopUp menu];
    while ([m numberOfItems] > 0)
        [m removeItemAtIndex:0];
    NSMenuItem *mi = [m addItemWithTitle:@"Add New Directory..." action:@selector(askForDirectory:) keyEquivalent:@""];
    [mi setTarget:self];
    mi = [m addItemWithTitle:@"Add iTunes Directory" action:@selector(addiTunes:) keyEquivalent:@""];
    [mi setTarget:self];
    [m addItem:[NSMenuItem separatorItem]];
    [_recentDirectories fillMenu:m];
    [addButtonPopUp selectItem: nil];
    [[addButtonPopUp cell] performClickWithFrame:[sender frame] inView:[sender superview]];
}
@end
