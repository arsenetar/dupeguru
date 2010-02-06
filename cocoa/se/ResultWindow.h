/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

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
    NSString *_lastAction;
}
- (IBAction)resetColumnsToDefault:(id)sender;
- (IBAction)startDuplicateScan:(id)sender;
@end
