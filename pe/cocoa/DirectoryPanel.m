#import "DirectoryPanel.h"
#import "ProgressController.h"

static NSString* jobAddIPhoto = @"jobAddIPhoto";

@implementation DirectoryPanel
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
    if ([[ProgressController mainProgressController] jobId] == jobAddIPhoto)
    {
        [directories reloadData];
    }
}
@end
