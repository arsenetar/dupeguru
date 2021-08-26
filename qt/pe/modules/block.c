/* Created By: Virgil Dupras
 * Created On: 2010-01-31
 * Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
 *
 * This software is licensed under the "BSD" License as described in the
 *"LICENSE" file, which should be included with this package. The terms are also
 *available at http://www.hardcoded.net/licenses/bsd_license
 **/

#define PY_SSIZE_T_CLEAN
#include "Python.h"

/* It seems like MS VC defines min/max already */
#ifndef _MSC_VER
static int max(int a, int b) { return b > a ? b : a; }

static int min(int a, int b) { return b < a ? b : a; }
#endif

static PyObject *getblock(PyObject *image, int width, int height) {
  int pixel_count, red, green, blue, bytes_per_line;
  PyObject *pred, *pgreen, *pblue;
  PyObject *result;

  red = green = blue = 0;
  pixel_count = width * height;
  if (pixel_count) {
    PyObject *sipptr, *bits_capsule, *pi;
    char *s;
    int i;

    pi = PyObject_CallMethod(image, "bytesPerLine", NULL);
    bytes_per_line = PyLong_AsLong(pi);
    Py_DECREF(pi);

    sipptr = PyObject_CallMethod(image, "bits", NULL);
    bits_capsule = PyObject_CallMethod(sipptr, "ascapsule", NULL);
    Py_DECREF(sipptr);
    s = (char *)PyCapsule_GetPointer(bits_capsule, NULL);
    Py_DECREF(bits_capsule);
    /* Qt aligns all its lines on 32bit, which means that if the number of bytes
     *per line for image is not divisible by 4, there's going to be crap
     *inserted in "s" We have to take this into account when calculating offsets
     **/
    for (i = 0; i < height; i++) {
      int j;
      for (j = 0; j < width; j++) {
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

  pred = PyLong_FromLong(red);
  pgreen = PyLong_FromLong(green);
  pblue = PyLong_FromLong(blue);
  result = PyTuple_Pack(3, pred, pgreen, pblue);
  Py_DECREF(pred);
  Py_DECREF(pgreen);
  Py_DECREF(pblue);

  return result;
}

/* block_getblocks(QImage image, int block_count_per_side) -> [(int r, int g,
 *int b), ...]
 *
 * Compute blocks out of `image`. Note the use of min/max when compes the time
 *of computing widths and heights and positions. This is to cover the case where
 *the width or height of the image is smaller than `block_count_per_side`. In
 *these cases, blocks will be, of course, 1 pixel big. But also, because all
 *compared block lists are required to be of the same size, any block that has
 * no pixel to be assigned to will simply be assigned the last pixel. This is
 *why we have min(..., height-block_height-1) and stuff like that.
 **/
static PyObject *block_getblocks(PyObject *self, PyObject *args) {
  int block_count_per_side, width, height, block_width, block_height, ih;
  PyObject *image;
  PyObject *pi;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "Oi", &image, &block_count_per_side)) {
    return NULL;
  }

  pi = PyObject_CallMethod(image, "width", NULL);
  width = PyLong_AsLong(pi);
  Py_DECREF(pi);
  pi = PyObject_CallMethod(image, "height", NULL);
  height = PyLong_AsLong(pi);
  Py_DECREF(pi);

  if (!(width && height)) {
    return PyList_New(0);
  }

  block_width = max(width / block_count_per_side, 1);
  block_height = max(height / block_count_per_side, 1);

  result = PyList_New((Py_ssize_t)block_count_per_side * block_count_per_side);
  if (result == NULL) {
    return NULL;
  }

  for (ih = 0; ih < block_count_per_side; ih++) {
    int top, iw;
    top = min(ih * block_height, height - block_height - 1);
    for (iw = 0; iw < block_count_per_side; iw++) {
      int left;
      PyObject *pcrop;
      PyObject *pblock;

      left = min(iw * block_width, width - block_width - 1);
      pcrop = PyObject_CallMethod(image, "copy", "iiii", left, top, block_width,
                                  block_height);
      if (pcrop == NULL) {
        Py_DECREF(result);
        return NULL;
      }
      pblock = getblock(pcrop, block_width, block_height);
      Py_DECREF(pcrop);
      if (pblock == NULL) {
        Py_DECREF(result);
        return NULL;
      }
      PyList_SET_ITEM(result, ih * block_count_per_side + iw, pblock);
    }
  }

  return result;
}

static PyMethodDef BlockMethods[] = {
    {"getblocks", block_getblocks, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef BlockDef = {PyModuleDef_HEAD_INIT,
                                      "_block_qt",
                                      NULL,
                                      -1,
                                      BlockMethods,
                                      NULL,
                                      NULL,
                                      NULL,
                                      NULL};

PyObject *PyInit__block_qt(void) {
  PyObject *m = PyModule_Create(&BlockDef);
  if (m == NULL) {
    return NULL;
  }
  return m;
}