//  Created by Scott Stevenson on 9/28/07.
//
//  Personal site: http://theocacao.com/
//  Post for this sample: http://theocacao.com/document.page/497
//
//  The code in this project is intended to be used as a learning
//  tool for Cocoa programmers. You may freely use the code in
//  your own programs, but please do not use the code as-is in
//  other tutorials.

#import <Cocoa/Cocoa.h>


@interface NSImage (Extras)

// creates a copy of the current image while maintaining
// proportions. also centers image, if necessary

- (NSImage*)imageByScalingProportionallyToSize:(NSSize)aSize;

@end