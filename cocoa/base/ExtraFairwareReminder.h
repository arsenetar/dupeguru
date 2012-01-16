/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyExtraFairwareReminder.h"
#import "PyDupeGuru.h"

@interface ExtraFairwareReminder : NSWindowController
{
    IBOutlet NSButton *continueButton;
    
    PyExtraFairwareReminder *model;
    NSTimer *timer;
}
- (id)initWithApp:(PyDupeGuru *)aApp;
- (PyExtraFairwareReminder *)model;

- (void)start;
- (void)updateButton;
- (IBAction)continue:(id)sender;
- (IBAction)contribute:(id)sender;
@end
