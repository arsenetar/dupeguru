/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>

int main(int argc, char *argv[])
{
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    NSString *pluginPath = [[NSBundle mainBundle]
                                pathForResource:@"dg_cocoa"
                                         ofType:@"plugin"];
    NSBundle *pluginBundle = [NSBundle bundleWithPath:pluginPath];
    [pluginBundle load];
    [pool release];
    return NSApplicationMain(argc,  (const char **) argv);
}
