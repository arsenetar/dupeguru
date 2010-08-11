# Created By: Virgil Dupras
# Created On: 2007/02/25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import logging
import multiprocessing
from collections import defaultdict, deque

from hscommon import job

from core.engine import Match
from .block import avgdiff, DifferentBlockCountError, NoBlocksError
from .cache import Cache

MIN_ITERATIONS = 3
BLOCK_COUNT_PER_SIDE = 15

# Enough so that we're sure that the main thread will not wait after a result.get() call
# cpucount*2 should be enough to be sure that the spawned process will not wait after the results
# collection made by the main process.
RESULTS_QUEUE_LIMIT = multiprocessing.cpu_count() * 2

def prepare_pictures(pictures, cache_path, j=job.nulljob):
    # The MemoryError handlers in there use logging without first caring about whether or not
    # there is enough memory left to carry on the operation because it is assumed that the
    # MemoryError happens when trying to read an image file, which is freed from memory by the
    # time that MemoryError is raised.
    cache = Cache(cache_path)
    prepared = [] # only pictures for which there was no error getting blocks
    try:
        for picture in j.iter_with_progress(pictures, 'Analyzed %d/%d pictures'):
            picture.dimensions
            picture.unicode_path = str(picture.path)
            try:
                if picture.unicode_path not in cache:
                    blocks = picture.get_blocks(BLOCK_COUNT_PER_SIDE)
                    cache[picture.unicode_path] = blocks
                prepared.append(picture)
            except (IOError, ValueError) as e:
                logging.warning(str(e))
            except MemoryError:
                logging.warning('Ran out of memory while reading %s of size %d' % (picture.unicode_path, picture.size))
                if picture.size < 10 * 1024 * 1024: # We're really running out of memory
                    raise
    except MemoryError:
        logging.warning('Ran out of memory while preparing pictures')
    cache.close()
    return prepared

def get_match(first, second, percentage):
    if percentage < 0:
        percentage = 0
    return Match(first, second, percentage)

def async_compare(ref_id, other_ids, dbname, threshold):
    cache = Cache(dbname)
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
    cache.close()
    return results
    
def getmatches(pictures, cache_path, threshold=75, match_scaled=False, j=job.nulljob):
    j = j.start_subjob([3, 7])
    pictures = prepare_pictures(pictures, cache_path, j)
    j = j.start_subjob([9, 1], 'Preparing for matching')
    cache = Cache(cache_path)
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
    cache.close()
    pictures = [p for p in pictures if hasattr(p, 'cache_id')]
    pool = multiprocessing.Pool()
    async_results = deque()
    matches = []
    pictures_copy = set(pictures)
    for ref in j.iter_with_progress(pictures, 'Matched %d/%d pictures'):
        others = pictures_copy if match_scaled else dimensions2pictures[ref.dimensions]
        others.remove(ref)
        if ref.is_ref:
            # Don't spend time comparing two ref pics together.
            others = [pic for pic in others if not pic.is_ref]
        if others:
            cache_ids = [f.cache_id for f in others]
            # We limit the number of cache_ids we send for multi-processing because otherwise, we
            # might get an error saying "String or BLOB exceeded size limit"
            ARG_LIMIT = 1000
            while cache_ids:
                args = (ref.cache_id, cache_ids[:ARG_LIMIT], cache_path, threshold)
                async_results.append(pool.apply_async(async_compare, args))
                cache_ids = cache_ids[ARG_LIMIT:]
        # We use a while here because it's possible that more than one result has been added if
        # ARG_LIMIT has been reached.
        while len(async_results) > RESULTS_QUEUE_LIMIT:
            result = async_results.popleft()
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