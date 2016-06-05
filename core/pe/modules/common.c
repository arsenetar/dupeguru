/* Created By: Virgil Dupras
 * Created On: 2010-02-04
 * Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
 *
 * This software is licensed under the "BSD" License as described in the "LICENSE" file, 
 * which should be included with this package. The terms are also available at 
 * http://www.hardcoded.net/licenses/bsd_license
 */

#include "common.h"

#ifndef _MSC_VER
int max(int a, int b)
{
    return b > a ? b : a;
}

int min(int a, int b)
{
    return b < a ? b : a;
}
#endif

PyObject* inttuple(int n, ...)
{
    int i;
    PyObject *pnumber;
    PyObject *result;
    va_list numbers;
    
    va_start(numbers, n);
    result = PyTuple_New(n);
    
    for (i=0; i<n; i++) {
        pnumber = PyLong_FromLong(va_arg(numbers, long));
        if (pnumber == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, i, pnumber);
    }
    
    va_end(numbers);
    return result;
}
