/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>

@interface NSEvent(NSEventAdditions)
- (unichar)firstCharacter;
- (NSUInteger)flags;
- (NSUInteger)modifierKeysFlags;
- (BOOL)isDeleteOrBackspace;
- (BOOL)isReturnOrEnter;
- (BOOL)isTab;
- (BOOL)isBackTab;
- (BOOL)isSpace;
- (BOOL)isUp;
- (BOOL)isDown;
- (BOOL)isLeft;
- (BOOL)isRight;
@end
