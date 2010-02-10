/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "DirectoryPanel.h"
#import "ProgressController.h"

static NSString* jobAddIPhoto = @"jobAddIPhoto";

@implementation DirectoryPanelPE
- (id)initWithParentApp:(id)aParentApp
{
    self = [super initWithParentApp:aParentApp];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(jobCompleted:) name:JobCompletedNotification object:nil];
    return self;
}

- (IBAction)addiPhoto:(id)sender
{
    [[ProgressController mainProgressController] setJobDesc:@"Adding iPhoto Library..."];
    [[ProgressController mainProgressController] setJobId:jobAddIPhoto];
    [[ProgressController mainProgressController] showSheetForParent:[self window]];
    [self addDirectory:@"iPhoto Library"];
}

- (IBAction)popupAddDirectoryMenu:(id)sender
{
    NSMenu *m = [addButtonPopUp menu];
    while ([m numberOfItems] > 0)
        [m removeItemAtIndex:0];
    NSMenuItem *mi = [m addItemWithTitle:@"Add New Directory..." action:@selector(askForDirectory:) keyEquivalent:@""];
    [mi setTarget:self];
    mi = [m addItemWithTitle:@"Add iPhoto Directory" action:@selector(addiPhoto:) keyEquivalent:@""];
    [mi setTarget:self];
    [m addItem:[NSMenuItem separatorItem]];
    [_recentDirectories fillMenu:m];
    [addButtonPopUp selectItem:nil];
    [[addButtonPopUp cell] performClickWithFrame:[sender frame] inView:[sender superview]];
}

- (void)jobCompleted:(NSNotification *)aNotification
{
    if ([[ProgressController mainProgressController] jobId] == jobAddIPhoto) {
        [outlineView reloadData];
    }
}
@end
