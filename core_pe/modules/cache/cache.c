/* Created By: Virgil Dupras
 * Created On: 2010-01-30
 * Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
 */
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"
#include "stdio.h"
#include "stdlib.h"

/* I know that there strtol out there, but it requires a pointer to
 * a char, which would in turn require me to buffer my chars around,
 * making the whole process slower.
 */
static long
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
    Py_ssize_t char_count, color_count, i;
    PyObject *result;
    if (!PyArg_ParseTuple(args, "s#", &s, &char_count)) {
        return NULL;
    }
    
    color_count = (char_count / 6);
    result = PyList_New(color_count);
    if (result == NULL) {
        return NULL;
    }
    
    for (i=0; i<color_count; i++) {
        long r, g, b;
        Py_ssize_t ci;
        PyObject *color_tuple;
        PyObject *pr, *pg, *pb;
        
        ci = i * 6;
        r = (xchar_to_long(s[ci]) << 4) + xchar_to_long(s[ci+1]);
        g = (xchar_to_long(s[ci+2]) << 4) + xchar_to_long(s[ci+3]);
        b = (xchar_to_long(s[ci+4]) << 4) + xchar_to_long(s[ci+5]);
        
        pr = PyInt_FromLong(r);
        pg = PyInt_FromLong(g);
        pb = PyInt_FromLong(b);
        if (pb == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        color_tuple = PyTuple_Pack(3, pr, pg, pb);
        if (color_tuple == NULL) {
            Py_DECREF(pr);
            Py_DECREF(pg);
            Py_DECREF(pb);
            Py_DECREF(result);
            return NULL;
        }
        PyList_SET_ITEM(result, i, color_tuple);
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
