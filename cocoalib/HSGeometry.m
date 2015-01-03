/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSGeometry.h"

CGFloat deg2rad(CGFloat deg)
{
    return deg * M_PI / 180;
}

CGFloat distance(NSPoint p1, NSPoint p2)
{
    CGFloat dX = p1.x - p2.x;
    CGFloat dY = p1.y - p2.y;
    return sqrt(dX * dX + dY * dY);
}

NSPoint pointInCircle(NSPoint center, CGFloat radius, CGFloat angle)
{
    // a/sin(A) = b/sin(B) = c/sin(C) = 2R
    // the start point it (center.x + radius, center.y) and goes counterclockwise
    angle = fmod(angle, M_PI*2);
    CGFloat C = M_PI/2;
    CGFloat A = fmod(angle, M_PI/2);
    CGFloat B = C - A;
    CGFloat c = radius;
    CGFloat ratio = c / sin(C);
    CGFloat b = ratio * sin(B);
    CGFloat a = ratio * sin(A);
    if (angle >= M_PI * 1.5)
        return NSMakePoint(center.x + a, center.y - b);
    else if (angle >= M_PI)
        return NSMakePoint(center.x - b, center.y - a);
    else if (angle >= M_PI/2)
        return NSMakePoint(center.x - a, center.y + b);
    else
        return NSMakePoint(center.x + b, center.y + a);
}

CGFloat angleFromPoints(NSPoint pt1, NSPoint pt2)
{
    // Returns the angle (radian) formed by the line pt1-pt2. The angle follows the same logic
    // as in pointInCircle.
    // What we do here is that we take the line and reduce it to fit a "unit circle" (circle with
    // a radius of 1). Then, either asin(adjusted_dy) or acos(adjusted_dx) will give us our angle.
    // We'll use asin(adjusted_dy).
    CGFloat length = distance(pt1, pt2);
    CGFloat dx = pt2.x - pt1.x;
    CGFloat dy = pt2.y - pt1.y;
    CGFloat ajdusted_dy = ABS(dy) / length;
    CGFloat angle = asin(ajdusted_dy);
    
    if ((dx < 0) && (dy >= 0)) {
        // top-left quadrant
        angle = M_PI - angle;
    }
    else if ((dx < 0) && (dy < 0)) {
        // bottom-left quadrant
        angle = M_PI + angle;
    }
    else if ((dx >= 0) && (dy < 0)) {
        // bottom-right quadrant
        angle = (2 * M_PI) - angle;
    }
    return angle;
}