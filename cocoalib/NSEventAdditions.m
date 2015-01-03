/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "NSEventAdditions.h"

@implementation NSEvent(NSEventAdditions)

- (unichar)firstCharacter
{
    NSString *characters = [self characters];
    if ([characters length] == 0)
    {
        return '\0';
    }
    return [characters characterAtIndex:0];
}

- (NSUInteger)flags
{
    // get flags and strip the lower 16 (device dependant) bits
    // See modifierFlags's doc for details
    return [self modifierFlags] & NSDeviceIndependentModifierFlagsMask;
}

- (NSUInteger)modifierKeysFlags
{
    // This is modifierFlags with only Command, Opt, Ctrl and Shift, without the rest of the flags
    // to pollute.
    return [self flags] & (NSShiftKeyMask | NSControlKeyMask | NSAlternateKeyMask | NSCommandKeyMask);
}

- (BOOL)isDeleteOrBackspace
{
    unichar firstChar = [self firstCharacter];
    return firstChar == NSDeleteFunctionKey || firstChar == NSDeleteCharFunctionKey || 
           firstChar == NSDeleteCharacter || firstChar == NSBackspaceCharacter;
}

- (BOOL)isReturnOrEnter
{
    unichar firstChar = [self firstCharacter];
    return firstChar == NSCarriageReturnCharacter || firstChar == NSEnterCharacter;
}

- (BOOL)isTab
{
    return [self firstCharacter] == NSTabCharacter;
}

- (BOOL)isBackTab
{
    return [self firstCharacter] == NSBackTabCharacter;
}

- (BOOL)isSpace
{
    return ([self firstCharacter] == 0x20) && (![self flags]);
}

- (BOOL)isUp
{
    return [self firstCharacter] == NSUpArrowFunctionKey;
}

- (BOOL)isDown
{
    return [self firstCharacter] == NSDownArrowFunctionKey;
}

- (BOOL)isLeft
{
    return [self firstCharacter] == NSLeftArrowFunctionKey;
}

- (BOOL)isRight
{
    return [self firstCharacter] == NSRightArrowFunctionKey;
}

@end
