/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "HSPyUtil.h"
#import "ObjP.h"

static NSString *gCocoaViewsModuleName;
void setCocoaViewsModuleName(NSString *moduleName)
{
    if (gCocoaViewsModuleName != nil) {
        [gCocoaViewsModuleName release];
    }
    gCocoaViewsModuleName = [moduleName retain];
}

PyObject* createCallback(NSString *aViewClassName, id aViewRef)
{
    NSString *moduleName;
    if (gCocoaViewsModuleName != nil) {
        moduleName = gCocoaViewsModuleName;
    }
    else {
        moduleName = @"inter.CocoaViews";
    }
    PyGILState_STATE gilState = PyGILState_Ensure();
    PyObject *pCallback = ObjP_classInstanceWithRef(aViewClassName, moduleName, aViewRef);
    PyGILState_Release(gilState);
    return pCallback;
}
