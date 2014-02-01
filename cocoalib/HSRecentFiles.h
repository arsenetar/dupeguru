/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>

@interface HSRecentFiles : NSObject
{
    id delegate;
    NSMenu *menu;
    NSString *name;
    NSMutableArray *filepaths;
    NSInteger numberOfMenuItemsToPreserve;
}
- (id)initWithName:(NSString *)aName menu:(NSMenu *)aMenu;

- (void)addFile:(NSString *)path;
- (void)rebuildMenu;
- (void)fillMenu:(NSMenu *)menu;
- (void)clearMenu:(id)sender;
- (void)menuClick:(id)sender;

- (NSMenu *)menu;
- (id)delegate;
- (void)setDelegate:(id)aDelegate;
- (NSArray *)filepaths;
@end

@protocol HSRecentFilesDelegate
- (void)recentFileClicked:(NSString *)path;
@end
