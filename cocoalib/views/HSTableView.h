/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "NSTableViewAdditions.h"

@class HSTableView;

@protocol HSTableViewDelegate <NSTableViewDelegate>
- (NSIndexSet *)selectedIndexes;
- (void)tableViewDidEndEditing:(HSTableView *)tableView;
- (void)tableViewCancelsEdition:(HSTableView *)tableView;
- (void)tableViewWasDoubleClicked:(HSTableView *)tableView;
@end

@interface HSTableView : NSTableView 
{
    BOOL manualEditionStop;
}
- (void)updateSelection;
- (void)stopEditing;
- (id <HSTableViewDelegate>)delegate;
- (void)setDelegate:(id <HSTableViewDelegate>)aDelegate;
- (NSScrollView *)wrapInScrollView;
@end

