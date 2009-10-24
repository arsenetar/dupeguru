# Created By: Virgil Dupras
# Created On: 2007/02/25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import logging
import multiprocessing
from Queue import Empty
from collections import defaultdict

from hsutil import job
from hsutil.misc import dedupe

from dupeguru.engine import Match
from .block import avgdiff, DifferentBlockCountError, NoBlocksError
from .cache import Cache

MIN_ITERATIONS = 3
BLOCK_COUNT_PER_SIDE = 15

# Enough so that we're sure that the main thread will not wait after a result.get() call
# cpucount*2 should be enough to be sure that the spawned process will not wait after the results
# collection made by the main process.
RESULTS_QUEUE_LIMIT = multiprocessing.cpu_count() * 2

def prepare_pictures(pictures, cached_blocks, j=job.nulljob):
    # The MemoryError handlers in there use logging without first caring about whether or not
    # there is enough memory left to carry on the operation because it is assumed that the
    # MemoryError happens when trying to read an image file, which is freed from memory by the
    # time that MemoryError is raised.
    prepared = [] # only pictures for which there was no error getting blocks
    try:
        for picture in j.iter_with_progress(pictures, 'Analyzed %d/%d pictures'):
            picture.dimensions
            picture.unicode_path = unicode(picture.path)
            try:
                if picture.unicode_path not in cached_blocks:
                    blocks = picture.get_blocks(BLOCK_COUNT_PER_SIDE)
                    cached_blocks[picture.unicode_path] = blocks
                prepared.append(picture)
            except IOError as e:
                logging.warning(unicode(e))
            except MemoryError:
                logging.warning(u'Ran out of memory while reading %s of size %d' % (picture.unicode_path, picture.size))
                if picture.size < 10 * 1024 * 1024: # We're really running out of memory
                    raise
    except MemoryError:
        logging.warning('Ran out of memory while preparing pictures')
    return prepared

def get_match(first, second, percentage):
    if percentage < 0:
        percentage = 0
    return Match(first, second, percentage)

def async_compare(ref_id, other_ids, dbname, threshold):
    cache = Cache(dbname, threaded=False)
    limit = 100 - threshold
    ref_blocks = cache[ref_id]
    pairs = cache.get_multiple(other_ids)
    results = []
    for other_id, other_blocks in pairs:
        try:
            diff = avgdiff(ref_blocks, other_blocks, limit, MIN_ITERATIONS)
            percentage = 100 - diff
        except (DifferentBlockCountError, NoBlocksError):
            percentage = 0
        if percentage >= threshold:
            results.append((ref_id, other_id, percentage))
    cache.con.close()
    return results
    
def getmatches(pictures, cached_blocks, threshold=75, match_scaled=False, j=job.nulljob):
    def empty_out_queue(queue, into):
        try:
            while True:
                into.append(queue.get(block=False))
        except Empty:
            pass
    
    j = j.start_subjob([3, 7])
    pictures = prepare_pictures(pictures, cached_blocks, j)
    j = j.start_subjob([9, 1], 'Preparing for matching')
    cache = cached_blocks
    id2picture = {}
    dimensions2pictures = defaultdict(set)
    for picture in pictures:
        try:
            picture.cache_id = cache.get_id(picture.unicode_path)
            id2picture[picture.cache_id] = picture
            if not match_scaled:
                dimensions2pictures[picture.dimensions].add(picture)
        except ValueError:
            pass
    pictures = [p for p in pictures if hasattr(p, 'cache_id')]
    pool = multiprocessing.Pool()
    async_results = []
    matches = []
    pictures_copy = set(pictures)
    for ref in j.iter_with_progress(pictures, 'Matched %d/%d pictures'):
        others = pictures_copy if match_scaled else dimensions2pictures[ref.dimensions]
        others.remove(ref)
        if others:
            cache_ids = [f.cache_id for f in others]
            args = (ref.cache_id, cache_ids, cached_blocks.dbname, threshold)
            async_results.append(pool.apply_async(async_compare, args))
        if len(async_results) > RESULTS_QUEUE_LIMIT:
            result = async_results.pop(0)
            matches.extend(result.get())
    for result in async_results: # process the rest of the results
        matches.extend(result.get())
    
    result = []
    for ref_id, other_id, percentage in j.iter_with_progress(matches, 'Verified %d/%d matches', every=10):
        ref = id2picture[ref_id]
        other = id2picture[other_id]
        if percentage == 100 and ref.md5 != other.md5:
            percentage = 99
        if percentage >= threshold:
            result.append(get_match(ref, other, percentage))
    return result

multiprocessing.freeze_support()