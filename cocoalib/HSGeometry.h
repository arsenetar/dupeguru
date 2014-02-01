/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import <math.h>

CGFloat deg2rad(CGFloat deg);
CGFloat distance(NSPoint p1, NSPoint p2);
NSPoint pointInCircle(NSPoint center, CGFloat radius, CGFloat angle);
CGFloat angleFromPoints(NSPoint pt1, NSPoint pt2);