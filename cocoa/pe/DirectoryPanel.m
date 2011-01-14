/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "DirectoryPanel.h"

@implementation DirectoryPanelPE
- (id)initWithParentApp:(id)aParentApp
{
    self = [super initWithParentApp:aParentApp];
    [[self window] setTitle:@"dupeGuru Picture Edition"];
    _alwaysShowPopUp = YES;
    return self;
}

- (void)fillPopUpMenu
{
    [super fillPopUpMenu];
    NSMenu *m = [addButtonPopUp menu];
    NSMenuItem *mi = [m insertItemWithTitle:@"Add iPhoto Library" action:@selector(addiPhoto:)
        keyEquivalent:@"" atIndex:1];
    [mi setTarget:self];
}

- (IBAction)addiPhoto:(id)sender
{
    [self addDirectory:@"iPhoto Library"];
}
@end
