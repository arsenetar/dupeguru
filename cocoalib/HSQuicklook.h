/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import <Quartz/Quartz.h>

@interface HSQLPreviewItem : NSObject <QLPreviewItem>
{
    NSURL *url;
    NSString *title;
}
- (id)initWithUrl:(NSURL *)aUrl title:(NSString *)aTitle;
@end