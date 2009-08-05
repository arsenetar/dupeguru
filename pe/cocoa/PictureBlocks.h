/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>


@interface PictureBlocks : NSObject {
}
+ (NSString *)getBlocksFromImagePath:(NSString *)imagePath blockCount:(NSNumber *)blockCount scanArea:(NSNumber *)scanArea;
+ (NSSize)getImageSize:(NSString *)imagePath;
@end


NSString* GetBlocks(NSString *filePath, int blockCount, int scanSize);