/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSErrorReportWindow.h"
#import "HSErrorReportWindow_UI.h"

@implementation HSErrorReportWindow

@synthesize contentTextView;
@synthesize githubUrl;

+ (void)showErrorReportWithContent:(NSString *)content githubUrl:(NSString *)githubUrl
{
    HSErrorReportWindow *report = [[HSErrorReportWindow alloc] initWithContent:content githubUrl:githubUrl];
    [NSApp runModalForWindow:[report window]];
    [report release];
}

- (id)initWithContent:(NSString *)content githubUrl:(NSString *)aGithubUrl
{
    self = [super initWithWindow:nil];
    [self setWindow:createHSErrorReportWindow_UI(self)];
    [contentTextView alignLeft:nil];
    [[[contentTextView textStorage] mutableString] setString:content];
    self.githubUrl = aGithubUrl;
    return self;
}

- (void)goToGithub
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:self.githubUrl]];
}

- (void)close
{
    [[self window] orderOut:self];
    [NSApp stopModalWithCode:NSOKButton];
}
@end