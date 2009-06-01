#import <Cocoa/Cocoa.h>


@interface PictureBlocks : NSObject {
}
+ (NSString *)getBlocksFromImagePath:(NSString *)imagePath blockCount:(NSNumber *)blockCount scanArea:(NSNumber *)scanArea;
+ (NSSize)getImageSize:(NSString *)imagePath;
@end


NSString* GetBlocks(NSString *filePath, int blockCount, int scanSize);