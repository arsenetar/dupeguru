/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
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
