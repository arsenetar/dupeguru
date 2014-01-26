# Created By: Virgil Dupras
# Created On: 2014-01-26
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import ftplib
import io
import time
import threading
import logging

def send_error_report(text):
    def do():
        try:
            conn = ftplib.FTP('drop.hardcoded.net')
            conn.login()
            conn.cwd('/drop')
            textfp = io.BytesIO(text.encode('utf-8'))
            cmd = 'STOR report%d.txt' % time.time()
            conn.storbinary(cmd, textfp)
        except Exception as e:
            logging.warning("Couldn't send error report: %s", e)

    threading.Thread(target=do).start()
