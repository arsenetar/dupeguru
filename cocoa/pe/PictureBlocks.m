/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "PictureBlocks.h"
#import "Utils.h"

@implementation PictureBlocks
+ (NSString *)getBlocksFromImagePath:(NSString *)imagePath blockCount:(NSNumber *)blockCount
{
    return GetBlocks(imagePath, n2i(blockCount));
}

+ (NSSize)getImageSize:(NSString *)imagePath
{
    CFURLRef fileURL = CFURLCreateWithFileSystemPath(NULL, (CFStringRef)imagePath, kCFURLPOSIXPathStyle, FALSE);
    CGImageSourceRef source = CGImageSourceCreateWithURL(fileURL, NULL);
    if (source == NULL)
        return NSMakeSize(0, 0);
    CGImageRef image = CGImageSourceCreateImageAtIndex(source, 0, NULL);
    if (image == NULL)
        return NSMakeSize(0, 0);
    size_t width = CGImageGetWidth(image);
    size_t height = CGImageGetHeight(image);
    CGImageRelease(image);
    CFRelease(source);
    CFRelease(fileURL);
    return NSMakeSize(width, height);
}
@end

 CGContextRef MyCreateBitmapContext (int width, int height) 
 {
     CGContextRef    context = NULL;
     CGColorSpaceRef colorSpace;
     void *          bitmapData;
     int             bitmapByteCount;
     int             bitmapBytesPerRow;
     
     bitmapBytesPerRow   = (width * 4);
     bitmapByteCount     = (bitmapBytesPerRow * height);
     
     colorSpace = CGColorSpaceCreateWithName(kCGColorSpaceGenericRGB);
     
     // calloc() must be used to allocate bitmapData here because the buffer has to be zeroed.
     // If it's not zeroes, when images with transparency are drawn in the context, this buffer
     // will stay with undefined pixels, which means that two pictures with the same pixels will
     // most likely have different blocks (which is not supposed to happen).
     bitmapData = calloc(bitmapByteCount, 1);
     if (bitmapData == NULL) 
     {
         fprintf (stderr, "Memory not allocated!");
         return NULL;
     }
     
     context = CGBitmapContextCreate (bitmapData,width,height,8,bitmapBytesPerRow,colorSpace,kCGImageAlphaNoneSkipLast);
     if (context== NULL)
     {
         free (bitmapData);
         fprintf (stderr, "Context not created!");
         return NULL;
     }
     CGColorSpaceRelease( colorSpace );
     return context;
 }
 
 // returns 0x00RRGGBB
 int GetBlock(unsigned char *imageData, int imageWidth, int imageHeight, int boxX, int boxY, int boxW, int boxH)
 {
     int i,j;
     int totalR = 0;
     int totalG = 0;
     int totalB = 0;
     for(i = boxY; i < boxY + boxH; i++)
     {
         for(j = boxX; j < boxX + boxW; j++)
         {
             int offset = (i * imageWidth * 4) + (j * 4);
             totalR += *(imageData + offset);
             totalG += *(imageData + offset + 1);
             totalB += *(imageData + offset + 2);
         }
     }
     int pixelCount = boxH * boxW;
     int result = 0;
     result += (totalR / pixelCount) << 16;
     result += (totalG / pixelCount) << 8;
     result += (totalB / pixelCount);
     return result;
 }
 
 NSString* GetBlocks (NSString* filePath, int blockCount) 
 {
     CFURLRef fileURL = CFURLCreateWithFileSystemPath(NULL, (CFStringRef)filePath, kCFURLPOSIXPathStyle, FALSE);
     CGImageSourceRef source = CGImageSourceCreateWithURL(fileURL, NULL);
     if (source == NULL)
         return NULL;
     CGImageRef image = CGImageSourceCreateImageAtIndex(source, 0, NULL);
     if (image == NULL)
         return NULL;
     size_t width = CGImageGetWidth(image);
     size_t height = CGImageGetHeight(image);
     CGContextRef myContext = MyCreateBitmapContext(width, height);
     CGRect myBoundingBox = CGRectMake (0, 0, width, height);
     CGContextDrawImage(myContext, myBoundingBox, image);
     unsigned char *bitmapData = CGBitmapContextGetData(myContext);
     if (bitmapData == NULL)
         return NULL;
     
     int blockHeight = height / blockCount;
     if (blockHeight < 1)
         blockHeight = 1;
     int blockWidth = width / blockCount;
     if (blockWidth < 1)
         blockWidth = 1;
     //blockCount might have changed
     int blockXCount = (width / blockWidth);
     int blockYCount = (height / blockHeight);
     
     CFMutableArrayRef blocks = CFArrayCreateMutable(NULL, blockXCount * blockYCount, &kCFTypeArrayCallBacks);
     int i,j;
     for(i = 0; i < blockYCount; i++)
     {
         for(j = 0; j < blockXCount; j++)
         {
             int block = GetBlock(bitmapData, width, height, j * blockWidth, i * blockHeight, blockWidth, blockHeight);
             CFStringRef strBlock = CFStringCreateWithFormat(NULL, NULL, CFSTR("%06x"), block);
             CFArrayAppendValue(blocks, strBlock);
             CFRelease(strBlock);
         }
     }
     
     CGContextRelease (myContext);
     if (bitmapData) free(bitmapData); 
     CGImageRelease(image);
     CFRelease(source);
     CFRelease(fileURL);
     
     CFStringRef result = CFStringCreateByCombiningStrings(NULL, blocks, CFSTR(""));
     CFRelease(blocks);
     return (NSString *)result;
 }