//  Created by Scott Stevenson on 9/28/07.
//
//  Personal site: http://theocacao.com/
//  Post for this sample: http://theocacao.com/document.page/497
//
//  The code in this project is intended to be used as a learning
//  tool for Cocoa programmers. You may freely use the code in
//  your own programs, but please do not use the code as-is in
//  other tutorials.

#import "NSImageAdditions.h"


@implementation NSImage (Extras)

- (NSImage*)imageByScalingProportionallyToSize:(NSSize)targetSize
{
    NSImage* sourceImage = self;
    NSImage* newImage = nil;
    
    if ([sourceImage isValid])
    {
        NSSize imageSize = [sourceImage size];
        CGFloat width  = imageSize.width;
        CGFloat height = imageSize.height;

        CGFloat targetWidth  = targetSize.width;
        CGFloat targetHeight = targetSize.height;

        // scaleFactor will be the fraction that we'll
        // use to adjust the size. For example, if we shrink
        // an image by half, scaleFactor will be 0.5. the
        // scaledWidth and scaledHeight will be the original,
        // multiplied by the scaleFactor.
        //
        // IMPORTANT: the "targetHeight" is the size of the space
        // we're drawing into. The "scaledHeight" is the height that
        // the image actually is drawn at, once we take into
        // account the ideal of maintaining proportions

        CGFloat scaleFactor  = 0.0;                
        CGFloat scaledWidth  = targetWidth;
        CGFloat scaledHeight = targetHeight;

        NSPoint thumbnailPoint = NSMakePoint(0,0);

        // since not all images are square, we want to scale
        // proportionately. To do this, we find the longest
        // edge and use that as a guide.

        if ( NSEqualSizes( imageSize, targetSize ) == NO )
        {            
            // use the longeset edge as a guide. if the
            // image is wider than tall, we'll figure out
            // the scale factor by dividing it by the
            // intended width. Otherwise, we'll use the
            // height.
            
            CGFloat widthFactor  = targetWidth / width;
            CGFloat heightFactor = targetHeight / height;
            
            if ( widthFactor < heightFactor )
                scaleFactor = widthFactor;
            else
                scaleFactor = heightFactor;

            // ex: 500 * 0.5 = 250 (newWidth)
            
            scaledWidth  = width  * scaleFactor;
            scaledHeight = height * scaleFactor;

            // center the thumbnail in the frame. if
            // wider than tall, we need to adjust the
            // vertical drawing point (y axis)
            
            if ( widthFactor < heightFactor )
                thumbnailPoint.y = (targetHeight - scaledHeight) * 0.5;
                
            else if ( widthFactor > heightFactor )
                thumbnailPoint.x = (targetWidth - scaledWidth) * 0.5;
        }


        // create a new image to draw into        
        newImage = [[NSImage alloc] initWithSize:targetSize];                                            

        // once focus is locked, all drawing goes into this NSImage instance
        // directly, not to the screen. It also receives its own graphics
        // context.
        //
        // Also, keep in mind that we're doing this in a background thread.
        // You only want to draw to the screen in the main thread, but
        // drawing to an offscreen image is (apparently) okay.

        [newImage lockFocus];

            NSRect thumbnailRect;
            thumbnailRect.origin = thumbnailPoint;
            thumbnailRect.size.width = scaledWidth;
            thumbnailRect.size.height = scaledHeight;

            [sourceImage drawInRect: thumbnailRect
                           fromRect: NSZeroRect
                          operation: NSCompositeSourceOver
                           fraction: 1.0];

        [newImage unlockFocus];
        
    }

    return [newImage autorelease];
}

@end