/* Created By: Virgil Dupras
 * Created On: 2010-01-31
 * Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
 *
 * This software is licensed under the "HS" License as described in the "LICENSE" file, 
 * which should be included with this package. The terms are also available at 
 * http://www.hardcoded.net/licenses/hs_license
 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"

/* It seems like MS VC defines min/max already */
#ifndef _MSC_VER
static int
max(int a, int b)
{
    return b > a ? b : a;
}

static int
min(int a, int b)
{
    return b < a ? b : a;
}
#endif

static PyObject*
getblock(PyObject *image)
{
    int width, height, pixel_count, red, green, blue, bytes_per_line;
    PyObject *pi, *pred, *pgreen, *pblue;
    PyObject *result;
    
    red = green = blue = 0;
    pi = PyObject_CallMethod(image, "width", NULL);
    width = PyInt_AsSsize_t(pi);
    Py_DECREF(pi);
    pi = PyObject_CallMethod(image, "height", NULL);
    height = PyInt_AsSsize_t(pi);
    Py_DECREF(pi);
    pixel_count = width * height;
    if (pixel_count) {
        PyObject *sipptr;
        char *s;
        int i;
        
        pi = PyObject_CallMethod(image, "bytesPerLine", NULL);
        bytes_per_line = PyInt_AsSsize_t(pi);
        Py_DECREF(pi);
        
        sipptr = PyObject_CallMethod(image, "bits", NULL);
        pi = PyObject_CallMethod(sipptr, "__int__", NULL);
        Py_DECREF(sipptr);
        s = (char *)PyInt_AsSsize_t(pi);
        Py_DECREF(pi);
        /* Qt aligns all its lines on 32bit, which means that if the number of bytes per
         * line for image is not divisible by 4, there's going to be crap inserted in "s"
         * We have to take this into account when calculating offsets
        **/
        for (i=0; i<height; i++) {
            int j;
            for (j=0; j<width; j++) {
                int offset;
                unsigned char r, g, b;
                
                offset = i * bytes_per_line + j * 3;
                r = s[offset];
                g = s[offset + 1];
                b = s[offset + 2];
                red += r;
                green += g;
                blue += b;
            }
        }
        
        red /= pixel_count;
        green /= pixel_count;
        blue /= pixel_count;
    }
    
    pred = PyInt_FromSsize_t(red);
    pgreen = PyInt_FromSsize_t(green);
    pblue = PyInt_FromSsize_t(blue);
    result = PyTuple_Pack(3, pred, pgreen, pblue);
    Py_DECREF(pred);
    Py_DECREF(pgreen);
    Py_DECREF(pblue);
    
    return result;
}

static PyObject*
block_getblocks(PyObject *self, PyObject *args)
{
    int block_count_per_side, width, height, block_width, block_height, ih;
    PyObject *image;
    PyObject *pi;
    PyObject *result;
    
    if (!PyArg_ParseTuple(args, "Oi", &image, &block_count_per_side)) {
        return NULL;
    }
    
    pi = PyObject_CallMethod(image, "width", NULL);
    width = PyInt_AsSsize_t(pi);
    Py_DECREF(pi);
    pi = PyObject_CallMethod(image, "height", NULL);
    height = PyInt_AsSsize_t(pi);
    Py_DECREF(pi);
    
    if (!(width && height)) {
        return PyList_New(0);
    }
    
    block_width = max(width / block_count_per_side, 1);
    block_height = max(height / block_count_per_side, 1);
    
    result = PyList_New(block_count_per_side * block_count_per_side);
    if (result == NULL) {
        return NULL;
    }
    
    for (ih=0; ih<block_count_per_side; ih++) {
        int top, iw;
        top = min(ih*block_height, height-block_height-1);
        for (iw=0; iw<block_count_per_side; iw++) {
            int left;
            PyObject *pcrop;
            PyObject *pblock;
            
            left = min(iw*block_width, width-block_width-1);
            pcrop = PyObject_CallMethod(image, "copy", "iiii", left, top, block_width, block_height);
            if (pcrop == NULL) {
                Py_DECREF(result);
                return NULL;
            }
            pblock = getblock(pcrop);
            Py_DECREF(pcrop);
            if (pblock == NULL) {
                Py_DECREF(result);
                return NULL;
            }
            PyList_SET_ITEM(result, ih*block_count_per_side+iw, pblock);
        }
    }
    
    return result;
}

static PyMethodDef BlockMethods[] = {
    {"getblocks",  block_getblocks, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyMODINIT_FUNC
init_block(void)
{
    PyObject *m = Py_InitModule("_block", BlockMethods);
    if (m == NULL) {
        return;
    }
}