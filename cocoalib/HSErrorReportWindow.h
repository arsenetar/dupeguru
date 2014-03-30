/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>

@interface HSErrorReportWindow : NSWindowController
{
    NSTextView *contentTextView;
    NSString *githubUrl;
}

@property (readwrite, retain) NSTextView *contentTextView;
@property (readwrite, retain) NSString *githubUrl;

// True if the user wants to send the report
+ (void)showErrorReportWithContent:(NSString *)content githubUrl:(NSString *)githubUrl;
- (id)initWithContent:(NSString *)content githubUrl:(NSString *)githubUrl;

- (void)goToGithub;
- (void)close;
@end