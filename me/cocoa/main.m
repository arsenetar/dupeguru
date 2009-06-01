//
//  main.m
//  dupeguru
//
//  Created by Virgil Dupras on 2006/02/01.
//  Copyright __MyCompanyName__ 2006. All rights reserved.
//

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
