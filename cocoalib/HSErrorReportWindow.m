/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "HSErrorReportWindow.h"
#import "HSErrorReportWindow_UI.h"

@implementation HSErrorReportWindow

@synthesize contentTextView;

+ (void)showErrorReportWithContent:(NSString *)content
{
    HSErrorReportWindow *report = [[HSErrorReportWindow alloc] initWithContent:content];
    [NSApp runModalForWindow:[report window]];
    [report release];
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
    NSString *text = [[contentTextView textStorage] string];
    NSString *URL = [NSString stringWithFormat:@"mailto:support@hardcoded.net?SUBJECT=Error Report&BODY=%@",text];
    NSString *encodedURL = [URL stringByAddingPercentEscapesUsingEncoding:NSUTF8StringEncoding];
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:encodedURL]];

    [[self window] orderOut:self];
    [NSApp stopModalWithCode:NSOKButton];
}

- (void)dontSend
{
    [[self window] orderOut:self];
    [NSApp stopModalWithCode:NSCancelButton];
}
@end