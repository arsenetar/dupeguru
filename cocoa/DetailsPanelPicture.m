/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "Utils.h"
#import "NSNotificationAdditions.h"
#import "NSImageAdditions.h"
#import "PyDupeGuru.h"
#import "DetailsPanelPicture.h"
#import "Consts.h"
#import "DetailsPanelPicture_UI.h"

@implementation DetailsPanelPicture

@synthesize dupeImage;
@synthesize dupeProgressIndicator;
@synthesize refImage;
@synthesize refProgressIndicator;

- (id)initWithApp:(PyDupeGuru *)aApp
{
    self = [super initWithPyRef:[aApp detailsPanel]];
    pyApp = aApp;
    _needsRefresh = YES;
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(imageLoaded:) name:ImageLoadedNotification object:self];
    return self;
}

- (NSWindow *)createWindow
{
    return createDetailsPanelPicture_UI(self);
}

- (void)loadImageAsync:(NSString *)imagePath
{
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    NSImage *image = [[NSImage alloc] initByReferencingFile:imagePath];
    NSImage *thumbnail = [image imageByScalingProportionallyToSize:NSMakeSize(512,512)];
    [image release];
    NSMutableDictionary *params = [NSMutableDictionary dictionary];
    [params setValue:imagePath forKey:@"imagePath"];
    [params setValue:thumbnail forKey:@"image"];
    [[NSNotificationCenter defaultCenter] postNotificationOnMainThreadWithName:ImageLoadedNotification object:self userInfo:params waitUntilDone:YES];
    [pool release];
}

- (void)refreshDetails
{
    if (!_needsRefresh)
        return;
    [detailsTable reloadData];
    
    NSString *refPath = [pyApp getSelectedDupeRefPath];
    if (_refPath != nil)
        [_refPath autorelease];
    _refPath = [refPath retain];
    [NSThread detachNewThreadSelector:@selector(loadImageAsync:) toTarget:self withObject:refPath];
    NSString *dupePath = [pyApp getSelectedDupePath];
    if (_dupePath != nil)
        [_dupePath autorelease];
    _dupePath = [dupePath retain];
    if (![dupePath isEqual: refPath])
        [NSThread detachNewThreadSelector:@selector(loadImageAsync:) toTarget:self withObject:dupePath];
    [refProgressIndicator startAnimation:nil];
    [dupeProgressIndicator startAnimation:nil];
    _needsRefresh = NO;
}

/* Notifications */
- (void)imageLoaded:(NSNotification *)aNotification
{
    NSString *imagePath = [[aNotification userInfo] valueForKey:@"imagePath"];
    NSImage *image = [[aNotification userInfo] valueForKey:@"image"];
    if ([imagePath isEqual: _refPath])
    {
        [refImage setImage:image];
        [refProgressIndicator stopAnimation:nil];
    }
    if ([imagePath isEqual: _dupePath])
    {
        [dupeImage setImage:image];
        [dupeProgressIndicator stopAnimation:nil];
    }
}

/* Python --> Cocoa */
- (void)refresh
{
    _needsRefresh = YES;
    [super refresh];
}
@end
