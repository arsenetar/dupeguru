/* Created By: Virgil Dupras
 * Created On: 2010-02-04
 * Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
 *
 * This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
 * which should be included with this package. The terms are also available at 
 * http://www.gnu.org/licenses/gpl-3.0.html
 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"

/* It seems like MS VC defines min/max already */
#ifndef _MSC_VER
int max(int a, int b);
int min(int a, int b);
#endif

/* Create a tuple out of an array of integers. */
PyObject* inttuple(int n, ...);