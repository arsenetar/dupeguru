/* Created By: Virgil Dupras
 * Created On: 2010-01-30
 * Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
 */
#include "Python.h"
#include "structmember.h"
#include "stdio.h"
#include "stdlib.h"

/* I know that there strtol out there, but it requires a pointer to
 * a char, which would in turn require me to buffer my chars around,
 * making the whole process slower.
 */
static inline long
xchar_to_long(char c)
{
    if ((c >= 48) && (c <= 57)) { /* 0-9 */
        return c - 48;
    }
    else if ((c >= 65) && (c <= 70)) { /* A-F */
        return c - 55;
    }
    else if ((c >= 97) && (c <= 102)) { /* a-f */
        return c - 87;
    }
    return 0;
}

static PyObject*
cache_string_to_colors(PyObject *self, PyObject *args)
{
    char *s;
    Py_ssize_t char_count;
    PyObject *result;
    int i;

    if (!PyArg_ParseTuple(args, "s#", &s, &char_count)) {
        return NULL;
    }
    
    result = PyList_New(0);
    if (result == NULL) {
        return NULL;
    }
    
    char_count = (char_count / 6) * 6;
    for (i=0; i<char_count; i+=6) {
        long r, g, b;
        PyObject *color_tuple;
        PyObject *pi;
        
        r = (xchar_to_long(s[i]) << 4) + xchar_to_long(s[i+1]);
        g = (xchar_to_long(s[i+2]) << 4) + xchar_to_long(s[i+3]);
        b = (xchar_to_long(s[i+4]) << 4) + xchar_to_long(s[i+5]);
        
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
