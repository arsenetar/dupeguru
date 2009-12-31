/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "../../cocoalib/Outline.h"
#import "../base/ResultWindow.h"
#import "DirectoryPanel.h"

@interface ResultWindow : ResultWindowBase
{
    IBOutlet NSSearchField *filterField;
    
    NSString *_lastAction;
    NSMutableIndexSet *_deltaColumns;
}
- (IBAction)clearIgnoreList:(id)sender;
- (IBAction)filter:(id)sender;
- (IBAction)ignoreSelected:(id)sender;
- (IBAction)markAll:(id)sender;
- (IBAction)markInvert:(id)sender;
- (IBAction)markNone:(id)sender;
- (IBAction)markSelected:(id)sender;
- (IBAction)markToggle:(id)sender;
- (IBAction)openSelected:(id)sender;
- (IBAction)refresh:(id)sender;
- (IBAction)removeDeadTracks:(id)sender;
- (IBAction)removeMarked:(id)sender;
- (IBAction)removeSelected:(id)sender;
- (IBAction)renameSelected:(id)sender;
- (IBAction)revealSelected:(id)sender;
- (IBAction)startDuplicateScan:(id)sender;
- (IBAction)toggleDelta:(id)sender;
@end
