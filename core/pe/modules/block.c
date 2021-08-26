/* Created By: Virgil Dupras
 * Created On: 2010-01-30
 * Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
 *
 * This software is licensed under the "BSD" License as described in the
 * "LICENSE" file, which should be included with this package. The terms are
 * also available at http://www.hardcoded.net/licenses/bsd_license
 */

#include "common.h"

/* avgdiff/maxdiff has been called with empty lists */
static PyObject *NoBlocksError;
/* avgdiff/maxdiff has been called with 2 block lists of different size. */
static PyObject *DifferentBlockCountError;

/* Returns a 3 sized tuple containing the mean color of 'image'.
 * image: a PIL image or crop.
 */
static PyObject *getblock(PyObject *image) {
  int i, totr, totg, totb;
  Py_ssize_t pixel_count;
  PyObject *ppixels;

  totr = totg = totb = 0;
  ppixels = PyObject_CallMethod(image, "getdata", NULL);
  if (ppixels == NULL) {
    return NULL;
  }

  pixel_count = PySequence_Length(ppixels);
  for (i = 0; i < pixel_count; i++) {
    PyObject *ppixel, *pr, *pg, *pb;
    int r, g, b;

    ppixel = PySequence_ITEM(ppixels, i);
    pr = PySequence_ITEM(ppixel, 0);
    pg = PySequence_ITEM(ppixel, 1);
    pb = PySequence_ITEM(ppixel, 2);
    Py_DECREF(ppixel);
    r = PyLong_AsLong(pr);
    g = PyLong_AsLong(pg);
    b = PyLong_AsLong(pb);
    Py_DECREF(pr);
    Py_DECREF(pg);
    Py_DECREF(pb);

    totr += r;
    totg += g;
    totb += b;
  }

  Py_DECREF(ppixels);

  if (pixel_count) {
    totr /= pixel_count;
    totg /= pixel_count;
    totb /= pixel_count;
  }

  return inttuple(3, totr, totg, totb);
}

/* Returns the difference between the first block and the second.
 * It returns an absolute sum of the 3 differences (RGB).
 */
static int diff(PyObject *first, PyObject *second) {
  int r1, g1, b1, r2, b2, g2;
  PyObject *pr, *pg, *pb;
  pr = PySequence_ITEM(first, 0);
  pg = PySequence_ITEM(first, 1);
  pb = PySequence_ITEM(first, 2);
  r1 = PyLong_AsLong(pr);
  g1 = PyLong_AsLong(pg);
  b1 = PyLong_AsLong(pb);
  Py_DECREF(pr);
  Py_DECREF(pg);
  Py_DECREF(pb);

  pr = PySequence_ITEM(second, 0);
  pg = PySequence_ITEM(second, 1);
  pb = PySequence_ITEM(second, 2);
  r2 = PyLong_AsLong(pr);
  g2 = PyLong_AsLong(pg);
  b2 = PyLong_AsLong(pb);
  Py_DECREF(pr);
  Py_DECREF(pg);
  Py_DECREF(pb);

  return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2);
}

PyDoc_STRVAR(block_getblocks2_doc,
             "Returns a list of blocks (3 sized tuples).\n\
\n\
image: A PIL image to base the blocks on.\n\
block_count_per_side: This integer determine the number of blocks the function will return.\n\
If it is 10, for example, 100 blocks will be returns (10 width, 10 height). The blocks will not\n\
necessarely cover square areas. The area covered by each block will be proportional to the image\n\
itself.\n");

static PyObject *block_getblocks2(PyObject *self, PyObject *args) {
  int block_count_per_side, width, height, block_width, block_height, ih;
  PyObject *image;
  PyObject *pimage_size, *pwidth, *pheight;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "Oi", &image, &block_count_per_side)) {
    return NULL;
  }

  pimage_size = PyObject_GetAttrString(image, "size");
  pwidth = PySequence_ITEM(pimage_size, 0);
  pheight = PySequence_ITEM(pimage_size, 1);
  width = PyLong_AsLong(pwidth);
  height = PyLong_AsLong(pheight);
  Py_DECREF(pimage_size);
  Py_DECREF(pwidth);
  Py_DECREF(pheight);

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
    int top, bottom, iw;
    top = min(ih * block_height, height - block_height);
    bottom = top + block_height;
    for (iw = 0; iw < block_count_per_side; iw++) {
      int left, right;
      PyObject *pbox;
      PyObject *pmethodname;
      PyObject *pcrop;
      PyObject *pblock;

      left = min(iw * block_width, width - block_width);
      right = left + block_width;
      pbox = inttuple(4, left, top, right, bottom);
      pmethodname = PyUnicode_FromString("crop");
      pcrop = PyObject_CallMethodObjArgs(image, pmethodname, pbox, NULL);
      Py_DECREF(pmethodname);
      Py_DECREF(pbox);
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
      PyList_SET_ITEM(result, ih * block_count_per_side + iw, pblock);
    }
  }

  return result;
}

PyDoc_STRVAR(block_avgdiff_doc,
             "Returns the average diff between first blocks and seconds.\n\
\n\
If the result surpasses limit, limit + 1 is returned, except if less than min_iterations\n\
iterations have been made in the blocks.\n");

static PyObject *block_avgdiff(PyObject *self, PyObject *args) {
  PyObject *first, *second;
  int limit, min_iterations;
  Py_ssize_t count;
  int sum, i, result;

  if (!PyArg_ParseTuple(args, "OOii", &first, &second, &limit,
                        &min_iterations)) {
    return NULL;
  }

  count = PySequence_Length(first);
  if (count != PySequence_Length(second)) {
    PyErr_SetString(DifferentBlockCountError, "");
    return NULL;
  }
  if (!count) {
    PyErr_SetString(NoBlocksError, "");
    return NULL;
  }

  sum = 0;
  for (i = 0; i < count; i++) {
    int iteration_count;
    PyObject *item1, *item2;

    iteration_count = i + 1;
    item1 = PySequence_ITEM(first, i);
    item2 = PySequence_ITEM(second, i);
    sum += diff(item1, item2);
    Py_DECREF(item1);
    Py_DECREF(item2);
    if ((sum > limit * iteration_count) &&
        (iteration_count >= min_iterations)) {
      return PyLong_FromLong(limit + 1);
    }
  }

  result = sum / count;
  if (!result && sum) {
    result = 1;
  }
  return PyLong_FromLong(result);
}

static PyMethodDef BlockMethods[] = {
    {"getblocks2", block_getblocks2, METH_VARARGS, block_getblocks2_doc},
    {"avgdiff", block_avgdiff, METH_VARARGS, block_avgdiff_doc},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef BlockDef = {PyModuleDef_HEAD_INIT,
                                      "_block",
                                      NULL,
                                      -1,
                                      BlockMethods,
                                      NULL,
                                      NULL,
                                      NULL,
                                      NULL};

PyObject *PyInit__block(void) {
  PyObject *m = PyModule_Create(&BlockDef);
  if (m == NULL) {
    return NULL;
  }

  NoBlocksError = PyErr_NewException("_block.NoBlocksError", NULL, NULL);
  PyModule_AddObject(m, "NoBlocksError", NoBlocksError);
  DifferentBlockCountError =
      PyErr_NewException("_block.DifferentBlockCountError", NULL, NULL);
  PyModule_AddObject(m, "DifferentBlockCountError", DifferentBlockCountError);

  return m;
}