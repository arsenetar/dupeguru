/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "HSErrorReportWindow.h"
#import "HSErrorReportWindow_UI.h"

@implementation HSErrorReportWindow

@synthesize contentTextView;

+ (BOOL)showErrorReportWithContent:(NSString *)content
{
    HSErrorReportWindow *report = [[HSErrorReportWindow alloc] initWithContent:content];
    NSInteger result = [NSApp runModalForWindow:[report window]];
    [report release];
    return result == NSOKButton;
}

- (id)initWithContent:(NSString *)content
{
    self = [super initWithWindow:nil];
    [self setWindow:createHSErrorReportWindow_UI(self)];
    [contentTextView alignLeft:nil];
    [[[contentTextView textStorage] mutableString] setString:content];
    return self;
}

- (void)send
{
    [[self window] orderOut:self];
    [NSApp stopModalWithCode:NSOKButton];
}

- (void)dontSend
{
    [[self window] orderOut:self];
    [NSApp stopModalWithCode:NSCancelButton];
}
@end