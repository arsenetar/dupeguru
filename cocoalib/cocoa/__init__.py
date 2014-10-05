# Created By: Virgil Dupras
# Created On: 2007-10-06
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

import logging
import time
import traceback
import sys

from .CocoaProxy import CocoaProxy

proxy = CocoaProxy()

def autoreleasepool(func):
    def wrapper(*args, **kwargs):
        proxy.createPool()
        try:
            func(*args, **kwargs)
        finally:
            proxy.destroyPool()
    return wrapper

def as_fetch(as_list, as_type, step_size=1000):
    """When fetching items from a very big list through applescript, the connection with the app
    will timeout. This function is to circumvent that. 'as_type' is the type of the items in the
    list (found in appscript.k). If we don't pass it to the 'each' arg of 'count()', it doesn't work.
    applescript is rather stupid..."""
    result = []
    # no timeout. default timeout is 60 secs, and it is reached for libs > 30k songs
    item_count = as_list.count(each=as_type, timeout=0)
    steps = item_count // step_size
    if item_count % step_size:
        steps += 1
    logging.info('Fetching %d items in %d steps' % (item_count, steps))
    # Don't forget that the indexes are 1-based and that the upper limit is included
    for step in range(steps):
        begin = step * step_size + 1
        end = min(item_count, begin + step_size - 1)
        if end > begin:
            result += as_list[begin:end](timeout=0)
        else: # When there is only one item, the stupid fuck gives it directly instead of putting it in a list.
            result.append(as_list[begin:end](timeout=0))
        time.sleep(.1)
    logging.info('%d items fetched' % len(result))
    return result

def extract_tb_noline(tb):
    # Same as traceback.extract_tb(), but without line fetching
    limit = 100
    list = []
    n = 0
    while tb is not None and (limit is None or n < limit):
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        list.append((filename, lineno, name, None))
        tb = tb.tb_next
        n = n+1
    return list

def safe_format_exception(type, value, tb):
    """Format exception from type, value and tb and fallback if there's a problem.

    In some cases in threaded exceptions under Cocoa, I get tracebacks targeting pyc files instead
    of py files, which results in traceback.format_exception() trying to print lines from pyc files
    and then crashing when trying to interpret that binary data as utf-8. We want a fallback in
    these cases.
    """
    try:
        return traceback.format_exception(type, value, tb)
    except Exception:
        result = ['Traceback (most recent call last):\n']
        result.extend(traceback.format_list(extract_tb_noline(tb)))
        result.extend(traceback.format_exception_only(type, value))
        return result

def install_exception_hook(github_url):
    def report_crash(type, value, tb):
        app_identifier = proxy.bundleIdentifier()
        app_version = proxy.appVersion()
        osx_version = proxy.osxVersion()
        s = "Application Identifier: {}\n".format(app_identifier)
        s += "Application Version: {}\n".format(app_version)
        s += "Mac OS X Version: {}\n\n".format(osx_version)
        s += ''.join(safe_format_exception(type, value, tb))
        if LOG_BUFFER:
            s += '\nRelevant Console logs:\n\n'
            s += '\n'.join(LOG_BUFFER)
        proxy.reportCrash_withGithubUrl_(s, github_url)

    sys.excepthook = report_crash

# A global log buffer to use for error reports
LOG_BUFFER = []

class CocoaHandler(logging.Handler):
    def emit(self, record):
        msg = record.getMessage()
        proxy.log_(msg)
        LOG_BUFFER.append(msg)
        del LOG_BUFFER[:-20]

def install_cocoa_logger():
    logging.getLogger().addHandler(CocoaHandler())

def patch_threaded_job_performer():
    # _async_run, under cocoa, has to be run within an autorelease pool to prevent leaks.
    # You only need this patch is you use one of CocoaProxy's function (which allocate objc
    # structures) inside a threaded job.
    from hscommon.jobprogress.performer import ThreadedJobPerformer
    ThreadedJobPerformer._async_run = autoreleasepool(ThreadedJobPerformer._async_run)

