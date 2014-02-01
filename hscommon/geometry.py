# Created By: Virgil Dupras
# Created On: 2011-08-05
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from sys import maxsize as INF
from math import sqrt

VERY_SMALL = 0.0000001

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return '<Point {:2.2f}, {:2.2f}>'.format(*self)
    
    def __iter__(self):
        yield self.x
        yield self.y
    
    def distance_to(self, other):
        return Line(self, other).length()
    

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    
    def __repr__(self):
        return '<Line {}, {}>'.format(*self)
    
    def __iter__(self):
        yield self.p1
        yield self.p2
    
    def dx(self):
        return self.p2.x - self.p1.x
    
    def dy(self):
        return self.p2.y - self.p1.y
    
    def length(self):
        return sqrt(self.dx() ** 2 + self.dy() ** 2)
    
    def slope(self):
        if self.dx() == 0:
            return INF if self.dy() > 0 else -INF
        else:
            return self.dy() / self.dx()
    
    def intersection_point(self, other):
        # with help from http://paulbourke.net/geometry/lineline2d/
        if abs(self.slope() - other.slope()) < VERY_SMALL:
            # parallel. Even if coincident, we return nothing
            return None
        
        A, B = self
        C, D = other
        
        denom  = (D.y-C.y) * (B.x-A.x) - (D.x-C.x) * (B.y-A.y)
        if denom == 0:
            return None
        numera = (D.x-C.x) * (A.y-C.y) - (D.y-C.y) * (A.x-C.x)
        numerb = (B.x-A.x) * (A.y-C.y) - (B.y-A.y) * (A.x-C.x)
        
        mua = numera / denom;
        mub = numerb / denom;
        if (0 <= mua <= 1) and (0 <= mub <= 1):
            x = A.x + mua * (B.x - A.x)
            y = A.y + mua * (B.y - A.y)
            return Point(x, y)
        else:
            return None
    

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.w
        yield self.h
    
    def __repr__(self):
        return '<Rect {:2.2f}, {:2.2f}, {:2.2f}, {:2.2f}>'.format(*self)
    
    @classmethod
    def from_center(cls, center, width, height):
        x = center.x - width / 2
        y = center.y - height / 2
        return cls(x, y, width, height)
    
    @classmethod
    def from_corners(cls, pt1, pt2):
        x1, y1 = pt1
        x2, y2 = pt2
        return cls(min(x1, x2), min(y1, y2), abs(x1-x2), abs(y1-y2))
    
    def center(self):
        return Point(self.x + self.w/2, self.y + self.h/2)
    
    def contains_point(self, point):
        x, y = point
        (x1, y1), (x2, y2) = self.corners()
        return (x1 <= x <= x2) and (y1 <= y <= y2)
    
    def contains_rect(self, rect):
        pt1, pt2 = rect.corners()
        return self.contains_point(pt1) and self.contains_point(pt2)
    
    def corners(self):
        return Point(self.x, self.y), Point(self.x+self.w, self.y+self.h)
    
    def intersects(self, other):
        r1pt1, r1pt2 = self.corners()
        r2pt1, r2pt2 = other.corners()
        if r1pt1.x < r2pt1.x:
            xinter = r1pt2.x >= r2pt1.x
        else:
            xinter = r2pt2.x >= r1pt1.x
        if not xinter:
            return False
        if r1pt1.y < r2pt1.y:
            yinter = r1pt2.y >= r2pt1.y
        else:
            yinter = r2pt2.y >= r1pt1.y
        return yinter
    
    def lines(self):
        pt1, pt4 = self.corners()
        pt2 = Point(pt4.x, pt1.y)
        pt3 = Point(pt1.x, pt4.y)
        l1 = Line(pt1, pt2)
        l2 = Line(pt2, pt4)
        l3 = Line(pt3, pt4)
        l4 = Line(pt1, pt3)
        return l1, l2, l3, l4
    
    def scaled_rect(self, dx, dy):
        """Returns a rect that has the same borders at self, but grown/shrunk by dx/dy on each side.
        """
        x, y, w, h = self
        x -= dx
        y -= dy
        w += dx * 2
        h += dy * 2
        return Rect(x, y, w, h)
    
    def united(self, other):
        """Returns the bounding rectangle of this rectangle and `other`.
        """
        # ul=upper left lr=lower right
        ulcorner1, lrcorner1 = self.corners()
        ulcorner2, lrcorner2 = other.corners()
        corner1 = Point(min(ulcorner1.x, ulcorner2.x), min(ulcorner1.y, ulcorner2.y))
        corner2 = Point(max(lrcorner1.x, lrcorner2.x), max(lrcorner1.y, lrcorner2.y))
        return Rect.from_corners(corner1, corner2)
    
    #--- Properties
    @property
    def top(self):
        return self.y
    
    @top.setter
    def top(self, value):
        self.y = value
    
    @property
    def bottom(self):
        return self.y + self.h
    
    @bottom.setter
    def bottom(self, value):
        self.y = value - self.h
    
    @property
    def left(self):
        return self.x
    
    @left.setter
    def left(self, value):
        self.x = value
    
    @property
    def right(self):
        return self.x + self.w
    
    @right.setter
    def right(self, value):
        self.x = value - self.w
    
    @property
    def width(self):
        return self.w
    
    @width.setter
    def width(self, value):
        self.w = value
    
    @property
    def height(self):
        return self.h
    
    @height.setter
    def height(self, value):
        self.h = value
    
