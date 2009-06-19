# Unit Name: dupeguru_pe.matchbase
# Created By: Virgil Dupras
# Created On: 2007/02/25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

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

def get_match(first,second,percentage):
    if percentage < 0:
        percentage = 0
    return Match(first,second,percentage)

class MatchFactory(object):
    cached_blocks = None
    block_count_per_side = 15
    threshold = 75
    match_scaled = False
    
    def _do_getmatches(self, files, j):
        raise NotImplementedError()
    
    def getmatches(self, files, j=job.nulljob):
        # The MemoryError handlers in there use logging without first caring about whether or not
        # there is enough memory left to carry on the operation because it is assumed that the
        # MemoryError happens when trying to read an image file, which is freed from memory by the
        # time that MemoryError is raised.
        j = j.start_subjob([2, 8])
        logging.info('Preparing %d files' % len(files))
        prepared = self.prepare_files(files, j)
        logging.info('Finished preparing %d files' % len(prepared))
        return self._do_getmatches(prepared, j)
    
    def prepare_files(self, files, j=job.nulljob):
        prepared = [] # only files for which there was no error getting blocks
        try:
            for picture in j.iter_with_progress(files, 'Analyzed %d/%d pictures'):
                picture.dimensions
                picture.unicode_path = unicode(picture.path)
                try:
                    if picture.unicode_path not in self.cached_blocks:
                        blocks = picture.get_blocks(self.block_count_per_side)
                        self.cached_blocks[picture.unicode_path] = blocks
                    prepared.append(picture)
                except IOError as e:
                    logging.warning(unicode(e))
                except MemoryError:
                    logging.warning(u'Ran out of memory while reading %s of size %d' % (picture.unicode_path, picture.size))
                    if picture.size < 10 * 1024 * 1024: # We're really running out of memory
                        raise
        except MemoryError:
            logging.warning('Ran out of memory while preparing files')
        return prepared
    

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

class AsyncMatchFactory(MatchFactory):
    def _do_getmatches(self, pictures, j):
        def empty_out_queue(queue, into):
            try:
                while True:
                    into.append(queue.get(block=False))
            except Empty:
                pass
        
        j = j.start_subjob([1, 8, 1], 'Preparing for matching')
        cache = self.cached_blocks
        id2picture = {}
        dimensions2pictures = defaultdict(set)
        for picture in pictures:
            try:
                picture.cache_id = cache.get_id(picture.unicode_path)
                id2picture[picture.cache_id] = picture
                if not self.match_scaled:
                    dimensions2pictures[picture.dimensions].add(picture)
            except ValueError:
                pass
        pictures = [p for p in pictures if hasattr(p, 'cache_id')]
        pool = multiprocessing.Pool()
        async_results = []
        pictures_copy = set(pictures)
        for ref in j.iter_with_progress(pictures):
            others = pictures_copy if self.match_scaled else dimensions2pictures[ref.dimensions]
            others.remove(ref)
            if others:
                cache_ids = [f.cache_id for f in others]
                args = (ref.cache_id, cache_ids, self.cached_blocks.dbname, self.threshold)
                async_results.append(pool.apply_async(async_compare, args))
        
        matches = []
        for result in j.iter_with_progress(async_results, 'Matched %d/%d pictures'):
            matches.extend(result.get())
        
        result = []
        for ref_id, other_id, percentage in j.iter_with_progress(matches, 'Verified %d/%d matches', every=10):
            ref = id2picture[ref_id]
            other = id2picture[other_id]
            if percentage == 100 and ref.md5 != other.md5:
                percentage = 99
            if percentage >= self.threshold:
                result.append(get_match(ref, other, percentage))
        return result
    

multiprocessing.freeze_support()