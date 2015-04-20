/* Created By: Virgil Dupras
 * Created On: 2010-02-04
 * Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
 *
 * This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
 * which should be included with this package. The terms are also available at 
 * http://www.gnu.org/licenses/gpl-3.0.html
**/

#include "common.h"

#import <Foundation/Foundation.h>

#define RADIANS( degrees ) ( degrees * M_PI / 180 )

static CFStringRef
pystring2cfstring(PyObject *pystring)
{
    PyObject *encoded;
    UInt8 *s;
    CFIndex size;
    CFStringRef result;
    
    if (PyUnicode_Check(pystring)) {
        encoded = PyUnicode_AsUTF8String(pystring);
        if (encoded == NULL) {
            return NULL;
        }
    } else {
        encoded = pystring;
        Py_INCREF(encoded);
    }
    
    s = (UInt8*)PyBytes_AS_STRING(encoded);
    size = PyBytes_GET_SIZE(encoded);
    result = CFStringCreateWithBytes(NULL, s, size, kCFStringEncodingUTF8, FALSE);
    Py_DECREF(encoded);
    return result;
}

static PyObject* block_osx_get_image_size(PyObject *self, PyObject *args)
{
    PyObject *path;
    CFStringRef image_path;
    CFURLRef image_url;
    CGImageSourceRef source;
    CGImageRef image;
    long width, height;
    PyObject *pwidth, *pheight;
    PyObject *result;
    
    width = 0;
    height = 0;
    if (!PyArg_ParseTuple(args, "O", &path)) {
        return NULL;
    }
    
    image_path = pystring2cfstring(path);
    if (image_path == NULL) {
        return PyErr_NoMemory();
    }
    image_url = CFURLCreateWithFileSystemPath(NULL, image_path, kCFURLPOSIXPathStyle, FALSE);
    CFRelease(image_path);
    
    source = CGImageSourceCreateWithURL(image_url, NULL);
    CFRelease(image_url);
    if (source != NULL) {
        image = CGImageSourceCreateImageAtIndex(source, 0, NULL);
        if (image != NULL) {
            width = CGImageGetWidth(image);
            height = CGImageGetHeight(image);
            CGImageRelease(image);
        }
        CFRelease(source);
    }
    
    pwidth = PyLong_FromLong(width);
    if (pwidth == NULL) {
        return NULL;
    }
    pheight = PyLong_FromLong(height);
    if (pheight == NULL) {
        return NULL;
    }
    result = PyTuple_Pack(2, pwidth, pheight);
    Py_DECREF(pwidth);
    Py_DECREF(pheight);
    return result;
}

static CGContextRef
MyCreateBitmapContext(int width, int height) 
{
    CGContextRef context = NULL;
    CGColorSpaceRef colorSpace;
    void *bitmapData;
    int bitmapByteCount;
    int bitmapBytesPerRow;
    
    bitmapBytesPerRow = (width * 4);
    bitmapByteCount = (bitmapBytesPerRow * height);
    
    colorSpace = CGColorSpaceCreateWithName(kCGColorSpaceGenericRGB);
    
    // calloc() must be used to allocate bitmapData here because the buffer has to be zeroed.
    // If it's not zeroes, when images with transparency are drawn in the context, this buffer
    // will stay with undefined pixels, which means that two pictures with the same pixels will
    // most likely have different blocks (which is not supposed to happen).
    bitmapData = calloc(bitmapByteCount, 1);
    if (bitmapData == NULL) {
        fprintf(stderr, "Memory not allocated!");
        return NULL;
    }
    
    context = CGBitmapContextCreate(bitmapData, width, height, 8, bitmapBytesPerRow, colorSpace,
        (CGBitmapInfo)kCGImageAlphaNoneSkipLast);
    if (context== NULL) {
        free(bitmapData);
        fprintf(stderr, "Context not created!");
        return NULL;
    }
    CGColorSpaceRelease(colorSpace);
    return context;
}

static PyObject* getblock(unsigned char *imageData, int imageWidth, int imageHeight, int boxX, int boxY, int boxW, int boxH)
{
    int i,j, totalR, totalG, totalB;
    
    totalR = totalG = totalB = 0;
    for(i=boxY; i<boxY+boxH; i++) {
        for(j=boxX; j<boxX+boxW; j++) {
            int offset = (i * imageWidth * 4) + (j * 4);
            totalR += *(imageData + offset);
            totalG += *(imageData + offset + 1);
            totalB += *(imageData + offset + 2);
        }
    }
    int pixelCount = boxH * boxW;
    totalR /= pixelCount;
    totalG /= pixelCount;
    totalB /= pixelCount;
    
    return inttuple(3, totalR, totalG, totalB);
}

static PyObject* block_osx_getblocks(PyObject *self, PyObject *args)
{
    PyObject *path, *result;
    CFStringRef image_path;
    CFURLRef image_url;
    CGImageSourceRef source;
    CGImageRef image;
    size_t width, height, image_width, image_height;
    int block_count, block_width, block_height, orientation, i;
    
    if (!PyArg_ParseTuple(args, "Oii", &path, &block_count, &orientation)) {
        return NULL;
    }
    
    if (PySequence_Length(path) == 0) {
        PyErr_SetString(PyExc_ValueError, "empty path");
        return NULL;
    }
    
    if ((orientation > 8) || (orientation < 0)) {
        orientation = 0; // simplifies checks later since we can only have values in 0-8
    }
    
    image_path = pystring2cfstring(path);
    if (image_path == NULL) {
        return PyErr_NoMemory();
    }
    image_url = CFURLCreateWithFileSystemPath(NULL, image_path, kCFURLPOSIXPathStyle, FALSE);
    CFRelease(image_path);
    
    source = CGImageSourceCreateWithURL(image_url, NULL);
    CFRelease(image_url);
    if (source == NULL) {
        return PyErr_NoMemory();
    }

    image = CGImageSourceCreateImageAtIndex(source, 0, NULL);
    if (image == NULL) {
        CFRelease(source);
        return PyErr_NoMemory();
    }
    
    
    width = image_width = CGImageGetWidth(image);
    height = image_height = CGImageGetHeight(image);
    if (orientation >= 5) {
        // orientations 5-8 rotate the photo sideways, so we have to swap width and height
        width = image_height;
        height = image_width;
    }
    
    CGContextRef context = MyCreateBitmapContext(width, height);
    
    if (orientation == 2) {
        // Flip X
        CGContextTranslateCTM(context, width, 0);
        CGContextScaleCTM(context, -1, 1);
    }
    else if (orientation == 3) {
        // Rot 180
        CGContextTranslateCTM(context, width, height);
        CGContextRotateCTM(context, RADIANS(180)); 
    }
    else if (orientation == 4) {
        // Flip Y
        CGContextTranslateCTM(context, 0, height);
        CGContextScaleCTM(context, 1, -1);
    }
    else if (orientation == 5) {
        // Flip X + Rot CW 90
        CGContextTranslateCTM(context, width, 0);
        CGContextScaleCTM(context, -1, 1);
        CGContextTranslateCTM(context, 0, height);
        CGContextRotateCTM(context, RADIANS(-90));
    }
    else if (orientation == 6) {
        // Rot CW 90
        CGContextTranslateCTM(context, 0, height);
        CGContextRotateCTM(context, RADIANS(-90));
    }
    else if (orientation == 7) {
        // Rot CCW 90 + Flip X
        CGContextTranslateCTM(context, width, 0);
        CGContextScaleCTM(context, -1, 1);
        CGContextTranslateCTM(context, width, 0);
        CGContextRotateCTM(context, RADIANS(90));
    }
    else if (orientation == 8) {
        // Rot CCW 90
        CGContextTranslateCTM(context, width, 0);
        CGContextRotateCTM(context, RADIANS(90));
    }
    CGRect myBoundingBox = CGRectMake(0, 0, image_width, image_height);
    CGContextDrawImage(context, myBoundingBox, image);
    unsigned char *bitmapData = CGBitmapContextGetData(context);
    CGContextRelease(context);
    
    CGImageRelease(image);
    CFRelease(source);
    if (bitmapData == NULL) {
        return PyErr_NoMemory();
    }
    
    block_width = max(width/block_count, 1);
    block_height = max(height/block_count, 1);
    
    result = PyList_New(block_count * block_count);
    if (result == NULL) {
        return NULL;
    }
    
    for(i=0; i<block_count; i++) {
        int j, top;
        top = min(i*block_height, height-block_height);
        for(j=0; j<block_count; j++) {
            int left;
            left = min(j*block_width, width-block_width);
            PyObject *block = getblock(bitmapData, width, height, left, top, block_width, block_height);
            if (block == NULL) {
                Py_DECREF(result);
                return NULL;
            }
            PyList_SET_ITEM(result, i*block_count+j, block);
        }
    }
    
    free(bitmapData); 
    return result;
}

static PyMethodDef BlockOsxMethods[] = {
    {"get_image_size",  block_osx_get_image_size, METH_VARARGS, ""},
    {"getblocks",  block_osx_getblocks, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef BlockOsxDef = {
    PyModuleDef_HEAD_INIT,
    "_block_osx",
    NULL,
    -1,
    BlockOsxMethods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyObject *
PyInit__block_osx(void)
{
    PyObject *m = PyModule_Create(&BlockOsxDef);
    if (m == NULL) {
        return NULL;
    }
    return m;
}