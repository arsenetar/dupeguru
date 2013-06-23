# Created By: Virgil Dupras
# Created On: 2010-01-31
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hashlib import md5

from ..testutil import CallLogger
from ..reg import RegistrableApplication, InvalidCodeError

def md5s(s):
    return md5(s.encode('utf-8')).hexdigest()

def assert_valid(appid, code, email):
    app = RegistrableApplication(CallLogger(), appid)
    try:
        app.validate_code(code, email)
    except InvalidCodeError as e:
        raise AssertionError("Registration failed: {0}".format(str(e)))

def assert_invalid(appid, code, email, msg_contains=None):
    app = RegistrableApplication(CallLogger(), appid)
    try:
        app.validate_code(code, email)
    except InvalidCodeError as e:
        if msg_contains:
            assert msg_contains in str(e)
    else:
        raise AssertionError("InvalidCodeError not raised")

def test_valid_code():
    email = 'foo@bar.com'
    appid = 42
    code = md5s('42' + email + '43' + 'aybabtu')
    assert_valid(appid, code, email)

def test_invalid_code():
    email = 'foo@bar.com'
    appid = 42
    code = md5s('43' + email + '43' + 'aybabtu')
    assert_invalid(appid, code, email)

def test_suggest_other_apps():
    # If a code is valid for another app, say so in the error message.
    email = 'foo@bar.com'
    appid = 42
    # 2 is moneyGuru's appid
    code = md5s('2' + email + '43' + 'aybabtu')
    assert_invalid(appid, code, email, msg_contains="moneyGuru")

def test_invert_code_and_email():
    # Try inverting code and email during validation in case the user mixed the fields up.
    # We still show an error here. It kind of sucks, but if we don't, the email and code fields
    # end up mixed up in the preferences. It's not as if this kind of error happened all the time...
    email = 'foo@bar.com'
    appid = 42
    code = md5s('42' + email + '43' + 'aybabtu')
    assert_invalid(appid, email, code, msg_contains="inverted")

def test_paypal_transaction():
    # If the code looks like a paypal transaction, mention it in the error message.
    email = 'foo@bar.com'
    appid = 42
    code = '2A693827WX9676888'
    assert_invalid(appid, code, email, 'Paypal transaction')
