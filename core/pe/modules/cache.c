/* Created By: Virgil Dupras
 * Created On: 2010-01-30
 * Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
 *
 * This software is licensed under the "BSD" License as described in the "LICENSE" file, 
 * which should be included with this package. The terms are also available at 
 * http://www.hardcoded.net/licenses/bsd_license
 */

#include "common.h"

static PyObject*
cache_bytes_to_colors(PyObject *self, PyObject *args)
{
    char *y;
    Py_ssize_t char_count, i, color_count;
    PyObject *result;
    unsigned long r, g, b;
    Py_ssize_t ci;
    PyObject *color_tuple;

    if (!PyArg_ParseTuple(args, "y#", &y, &char_count)) {
        return NULL;
    }
    
    color_count = char_count / 3;
    result = PyList_New(color_count);
    if (result == NULL) {
        return NULL;
    }
    
    for (i=0; i<color_count; i++) {
        ci = i * 3;
        r = (unsigned char) y[ci];
        g = (unsigned char) y[ci+1];
        b = (unsigned char) y[ci+2];
        
        color_tuple = inttuple(3, r, g, b);
        if (color_tuple == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyList_SET_ITEM(result, i, color_tuple);
    }
    
    return result;
}

static PyMethodDef CacheMethods[] = {
    {"bytes_to_colors",  cache_bytes_to_colors, METH_VARARGS, "Transform the bytes 's' into a list of 3 sized tuples."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef CacheDef = {
    PyModuleDef_HEAD_INIT,
    "_cache",
    NULL,
    -1,
    CacheMethods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyObject *
PyInit__cache(void)
{
    PyObject *m = PyModule_Create(&CacheDef);
    if (m == NULL) {
        return NULL;
    }
    return m;
}