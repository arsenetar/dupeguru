#import <Cocoa/Cocoa.h>

int main (int argc, const char * argv[]) {
    if(argc == 1){
        NSLog(@"A file path to send to trash is needed");
        return 1;
    }
    NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
    NSString *filepath = [NSString stringWithCString:argv[1] encoding:NSUTF8StringEncoding];
    NSLog(@"%@",filepath);
    NSMutableArray *split = [NSMutableArray arrayWithArray:[filepath componentsSeparatedByString:@"/"]];
    NSString *filename = [split lastObject];
    [split removeLastObject];
    NSString *dirpath = [split componentsJoinedByString:@"/"];
    int result;
    [[NSWorkspace sharedWorkspace] performFileOperation:NSWorkspaceRecycleOperation
                                                 source:dirpath 
                                            destination:@""
                                                  files:[NSArray arrayWithObject:filename]
                                                    tag:&result];
    [pool drain];
    return result;
}
