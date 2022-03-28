# Created By: Virgil Dupras
# Created On: 2007/02/25
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging
import multiprocessing
from itertools import combinations

from hscommon.util import extract, iterconsume
from hscommon.trans import tr
from hscommon.jobprogress import job

from core.engine import Match
from .block import avgdiff, DifferentBlockCountError, NoBlocksError

# OPTIMIZATION NOTES:
# The bottleneck of the matching phase is CPU, which is why we use multiprocessing. However, another
# bottleneck that shows up when a lot of pictures are involved is Disk IO's because blocks
# constantly have to be read from disks by subprocesses. This problem is especially big on CPUs
# with a lot of cores. Therefore, we must minimize Disk IOs. The best way to achieve that is to
# separate the files to scan in "chunks" and it's by chunk that blocks are read in memory and
# compared to each other. Each file in a chunk has to be compared to each other, of course, but also
# to files in other chunks. So chunkifying doesn't save us any actual comparison, but the advantage
# is that instead of reading blocks from disk number_of_files**2 times, we read it
# number_of_files*number_of_chunks times.
# Determining the right chunk size is tricky, bceause if it's too big, too many blocks will be in
# memory at the same time and we might end up with memory trashing, which is awfully slow. So,
# because our *real* bottleneck is CPU, the chunk size must simply be enough so that the CPU isn't
# starved by Disk IOs.

MIN_ITERATIONS = 3
BLOCK_COUNT_PER_SIDE = 15
DEFAULT_CHUNK_SIZE = 1000
MIN_CHUNK_SIZE = 100

# Enough so that we're sure that the main thread will not wait after a result.get() call
# cpucount+1 should be enough to be sure that the spawned process will not wait after the results
# collection made by the main process.
try:
    RESULTS_QUEUE_LIMIT = multiprocessing.cpu_count() + 1
except Exception:
    # I had an IOError on app launch once. It seems to be a freak occurrence. In any case, we want
    # the app to launch, so let's just put an arbitrary value.
    logging.warning("Had problems to determine cpu count on launch.")
    RESULTS_QUEUE_LIMIT = 8


def get_cache(cache_path, readonly=False):
    if cache_path.endswith("shelve"):
        from .cache_shelve import ShelveCache

        return ShelveCache(cache_path, readonly=readonly)
    else:
        from .cache_sqlite import SqliteCache

        return SqliteCache(cache_path, readonly=readonly)


def prepare_pictures(pictures, cache_path, with_dimensions, j=job.nulljob):
    # The MemoryError handlers in there use logging without first caring about whether or not
    # there is enough memory left to carry on the operation because it is assumed that the
    # MemoryError happens when trying to read an image file, which is freed from memory by the
    # time that MemoryError is raised.
    cache = get_cache(cache_path)
    cache.purge_outdated()
    prepared = []  # only pictures for which there was no error getting blocks
    try:
        for picture in j.iter_with_progress(pictures, tr("Analyzed %d/%d pictures")):
            if not picture.path:
                # XXX Find the root cause of this. I've received reports of crashes where we had
                # "Analyzing picture at " (without a path) in the debug log. It was an iPhoto scan.
                # For now, I'm simply working around the crash by ignoring those, but it would be
                # interesting to know exactly why this happens. I'm suspecting a malformed
                # entry in iPhoto library.
                logging.warning("We have a picture with a null path here")
                continue
            picture.unicode_path = str(picture.path)
            logging.debug("Analyzing picture at %s", picture.unicode_path)
            if with_dimensions:
                picture.dimensions  # pre-read dimensions
            try:
                if picture.unicode_path not in cache:
                    blocks = picture.get_blocks(BLOCK_COUNT_PER_SIDE)
                    cache[picture.unicode_path] = blocks
                prepared.append(picture)
            except (IOError, ValueError) as e:
                logging.warning(str(e))
            except MemoryError:
                logging.warning(
                    "Ran out of memory while reading %s of size %d",
                    picture.unicode_path,
                    picture.size,
                )
                if picture.size < 10 * 1024 * 1024:  # We're really running out of memory
                    raise
    except MemoryError:
        logging.warning("Ran out of memory while preparing pictures")
    cache.close()
    return prepared


def get_chunks(pictures):
    min_chunk_count = multiprocessing.cpu_count() * 2  # have enough chunks to feed all subprocesses
    chunk_count = len(pictures) // DEFAULT_CHUNK_SIZE
    chunk_count = max(min_chunk_count, chunk_count)
    chunk_size = (len(pictures) // chunk_count) + 1
    chunk_size = max(MIN_CHUNK_SIZE, chunk_size)
    logging.info(
        "Creating %d chunks with a chunk size of %d for %d pictures",
        chunk_count,
        chunk_size,
        len(pictures),
    )
    chunks = [pictures[i : i + chunk_size] for i in range(0, len(pictures), chunk_size)]
    return chunks


def get_match(first, second, percentage):
    if percentage < 0:
        percentage = 0
    return Match(first, second, percentage)


def async_compare(ref_ids, other_ids, dbname, threshold, picinfo):
    # The list of ids in ref_ids have to be compared to the list of ids in other_ids. other_ids
    # can be None. In this case, ref_ids has to be compared with itself
    # picinfo is a dictionary {pic_id: (dimensions, is_ref)}
    cache = get_cache(dbname, readonly=True)
    limit = 100 - threshold
    ref_pairs = list(cache.get_multiple(ref_ids))
    if other_ids is not None:
        other_pairs = list(cache.get_multiple(other_ids))
        comparisons_to_do = [(r, o) for r in ref_pairs for o in other_pairs]
    else:
        comparisons_to_do = list(combinations(ref_pairs, 2))
    results = []
    for (ref_id, ref_blocks), (other_id, other_blocks) in comparisons_to_do:
        ref_dimensions, ref_is_ref = picinfo[ref_id]
        other_dimensions, other_is_ref = picinfo[other_id]
        if ref_is_ref and other_is_ref:
            continue
        if ref_dimensions != other_dimensions:
            continue
        try:
            diff = avgdiff(ref_blocks, other_blocks, limit, MIN_ITERATIONS)
            percentage = 100 - diff
        except (DifferentBlockCountError, NoBlocksError):
            percentage = 0
        if percentage >= threshold:
            results.append((ref_id, other_id, percentage))
    cache.close()
    return results


def getmatches(pictures, cache_path, threshold, match_scaled=False, j=job.nulljob):
    def get_picinfo(p):
        if match_scaled:
            return (None, p.is_ref)
        else:
            return (p.dimensions, p.is_ref)

    def collect_results(collect_all=False):
        # collect results and wait until the queue is small enough to accomodate a new results.
        nonlocal async_results, matches, comparison_count, comparisons_to_do
        limit = 0 if collect_all else RESULTS_QUEUE_LIMIT
        while len(async_results) > limit:
            ready, working = extract(lambda r: r.ready(), async_results)
            for result in ready:
                matches += result.get()
                async_results.remove(result)
                comparison_count += 1
        # About the NOQA below: I think there's a bug in pyflakes. To investigate...
        progress_msg = tr("Performed %d/%d chunk matches") % (
            comparison_count,
            len(comparisons_to_do),
        )  # NOQA
        j.set_progress(comparison_count, progress_msg)

    j = j.start_subjob([3, 7])
    pictures = prepare_pictures(pictures, cache_path, with_dimensions=not match_scaled, j=j)
    j = j.start_subjob([9, 1], tr("Preparing for matching"))
    cache = get_cache(cache_path)
    id2picture = {}
    for picture in pictures:
        try:
            picture.cache_id = cache.get_id(picture.unicode_path)
            id2picture[picture.cache_id] = picture
        except ValueError:
            pass
    cache.close()
    pictures = [p for p in pictures if hasattr(p, "cache_id")]
    pool = multiprocessing.Pool()
    async_results = []
    matches = []
    chunks = get_chunks(pictures)
    # We add a None element at the end of the chunk list because each chunk has to be compared
    # with itself. Thus, each chunk will show up as a ref_chunk having other_chunk set to None once.
    comparisons_to_do = list(combinations(chunks + [None], 2))
    comparison_count = 0
    j.start_job(len(comparisons_to_do))
    try:
        for ref_chunk, other_chunk in comparisons_to_do:
            picinfo = {p.cache_id: get_picinfo(p) for p in ref_chunk}
            ref_ids = [p.cache_id for p in ref_chunk]
            if other_chunk is not None:
                other_ids = [p.cache_id for p in other_chunk]
                picinfo.update({p.cache_id: get_picinfo(p) for p in other_chunk})
            else:
                other_ids = None
            args = (ref_ids, other_ids, cache_path, threshold, picinfo)
            async_results.append(pool.apply_async(async_compare, args))
            collect_results()
        collect_results(collect_all=True)
    except MemoryError:
        # Rare, but possible, even in 64bit situations (ref #264). What do we do now? We free us
        # some wiggle room, log about the incident, and stop matching right here. We then process
        # the matches we have. The rest of the process doesn't allocate much and we should be
        # alright.
        del (
            comparisons_to_do,
            chunks,
            pictures,
        )  # some wiggle room for the next statements
        logging.warning("Ran out of memory when scanning! We had %d matches.", len(matches))
        del matches[-len(matches) // 3 :]  # some wiggle room to ensure we don't run out of memory again.
    pool.close()
    result = []
    myiter = j.iter_with_progress(
        iterconsume(matches, reverse=False),
        tr("Verified %d/%d matches"),
        every=10,
        count=len(matches),
    )
    for ref_id, other_id, percentage in myiter:
        ref = id2picture[ref_id]
        other = id2picture[other_id]
        if percentage == 100 and ref.digest != other.digest:
            percentage = 99
        if percentage >= threshold:
            ref.dimensions  # pre-read dimensions for display in results
            other.dimensions
            result.append(get_match(ref, other, percentage))
    pool.join()
    return result


multiprocessing.freeze_support()
