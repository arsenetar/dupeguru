/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSFairwareProtocol.h"

@interface HSFairwareReminder : NSObject
{
    NSWindow *codePanel;
    NSTextField *codePromptTextField;
    NSTextField *codeTextField;
    NSTextField *emailTextField;
    NSWindow *demoNagPanel;
    NSTextField *demoPromptTextField;
    
    id <HSFairwareProtocol> app;
}

@property (readwrite, retain) NSWindow *codePanel;
@property (readwrite, retain) NSTextField *codePromptTextField;
@property (readwrite, retain) NSTextField *codeTextField;
@property (readwrite, retain) NSTextField *emailTextField;
@property (readwrite, retain) NSWindow *demoNagPanel;
@property (readwrite, retain) NSTextField *demoPromptTextField;

//Show nag only if needed
+ (BOOL)showDemoNagWithApp:(id <HSFairwareProtocol>)app prompt:(NSString *)prompt;
- (id)initWithApp:(id <HSFairwareProtocol>)app;

- (void)contribute;
- (void)buy;
- (void)moreInfo;
- (void)cancelCode;
- (void)showEnterCode;
- (void)submitCode;
- (void)closeDialog;

- (BOOL)showNagPanel:(NSWindow *)panel; //YES: The code has been sucessfully submitted NO: The use wan't to try the demo.
- (BOOL)showDemoNagPanelWithPrompt:(NSString *)prompt;
- (NSInteger)enterCode; //returns the modal code.
@end
