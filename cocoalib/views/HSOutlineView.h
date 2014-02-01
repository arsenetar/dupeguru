/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "NSTableViewAdditions.h"
#import "NSIndexPathAdditions.h"

@class HSOutlineView;

@protocol HSOutlineViewDelegate <NSOutlineViewDelegate>
- (NSArray *)selectedIndexPaths; /* array of NSIndexPath* */
- (NSString *)dataForCopyToPasteboard;
- (NSIndexPath *)internalizedPath:(NSIndexPath *)path;
- (void)outlineViewDidEndEditing:(HSOutlineView *)outlineView;
- (void)outlineViewCancelsEdition:(HSOutlineView *)outlineView;
- (void)outlineViewWasDoubleClicked:(HSOutlineView *)outlineView;
@end

@interface HSOutlineView : NSOutlineView
{
    BOOL manualEditionStop;
    NSEvent *eventToIgnore;
}
- (id <HSOutlineViewDelegate>)delegate;
- (void)setDelegate:(id <HSOutlineViewDelegate>)aDelegate;
- (NSIndexPath *)selectedPath;
- (void)selectPath:(NSIndexPath *)aPath;
- (NSArray *)selectedNodePaths;
- (void)selectNodePaths:(NSArray *)nodePaths;
- (void)stopEditing;
- (void)updateSelection;
- (void)ignoreEventForEdition:(NSEvent *)aEvent;
- (void)ensureExpanded:(NSIndexPath *)aPath;

- (IBAction)copy:(id)sender;
@end
