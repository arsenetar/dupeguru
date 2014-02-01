/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>

/* This is a hack to easily get around a cocoa limitation

In some weird circumstances, NSOutlineView calls [item indexPath] to the item instances given to
it. I guess is expects eveyone to give it NSTreeNode instances. Anyway, because in MG, simple
NSIndexPath are used, it causes problems. Not anymore.
*/

@interface NSIndexPath(NSIndexPathAdditions)
- (NSIndexPath *)indexPath;
@end