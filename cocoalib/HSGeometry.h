/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import <math.h>

CGFloat deg2rad(CGFloat deg);
CGFloat distance(NSPoint p1, NSPoint p2);
NSPoint pointInCircle(NSPoint center, CGFloat radius, CGFloat angle);
CGFloat angleFromPoints(NSPoint pt1, NSPoint pt2);