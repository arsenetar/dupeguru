/* Created By: Virgil Dupras
 * Created On: 2010-01-30
 * Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
 */
#include "Python.h"
#include "structmember.h"

static PyObject*
cache_string_to_colors(PyObject *self, PyObject *args)
{
    char *s;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "s", &s)) {
        return NULL;
    }
    
    result = PyList_New(0);
    if (result == NULL) {
        return NULL;
    }
    
    while (*s) {
        long r, g, b, whole_color;
        char buffer[7];
        PyObject *color_tuple;
        PyObject *pi;
        
        strncpy(buffer, s, 6);
        if (strlen(buffer) < 6) { /* incomplete color, terminate loop */
            break;
        }
        s += 6;
        whole_color = strtol(buffer, NULL, 16);
        r = whole_color >> 16;
        g = (whole_color >> 8) & 0xff;
        b = whole_color & 0xff;
        
        color_tuple = PyTuple_New(3);
        pi = PyInt_FromLong(r);
        if (pi == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(color_tuple, 0, pi);
        pi = PyInt_FromLong(g);
        if (pi == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(color_tuple, 1, pi);
        pi = PyInt_FromLong(b);
        if (pi == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(color_tuple, 2, pi);
        
        if (PyList_Append(result, color_tuple) < 0) {
            Py_DECREF(result);
            return NULL;
        }
    }
    
    return result;
}

static PyMethodDef CacheMethods[] = {
    {"string_to_colors",  cache_string_to_colors, METH_VARARGS,
     "Transform the string 's' in a list of 3 sized tuples."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
init_cache(void)
{
    (void)Py_InitModule("_cache", CacheMethods);
}
