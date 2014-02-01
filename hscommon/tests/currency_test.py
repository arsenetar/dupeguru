# Created By: Virgil Dupras
# Created On: 2008-04-20
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date
import sqlite3 as sqlite

from ..testutil import eq_, assert_almost_equal
from ..currency import Currency, RatesDB, CAD, EUR, USD

PLN = Currency(code='PLN')

def setup_module(module):
    global FOO
    global BAR
    FOO = Currency.register('FOO', 'Currency with start date', start_date=date(2009, 1, 12), start_rate=2)
    BAR = Currency.register('BAR', 'Currency with stop date', stop_date=date(2010, 1, 12), latest_rate=2)

def teardown_module(module):
    # We must unset our test currencies or else we might mess up with other tests.
    from .. import currency
    import imp
    imp.reload(currency)

def teardown_function(function):
    Currency.set_rates_db(None)

def test_currency_creation():
    # Different ways to create a currency.
    eq_(Currency('CAD'), CAD)
    eq_(Currency(name='Canadian dollar'), CAD)

def test_currency_copy():
    # Currencies can be copied.
    import copy
    eq_(copy.copy(CAD), CAD)
    eq_(copy.deepcopy(CAD), CAD)

def test_get_rate_on_empty_db():
    # When there is no data available, use the start_rate.
    eq_(CAD.value_in(USD, date(2008, 4, 20)), 1 / USD.latest_rate)

def test_physical_rates_db_remember_rates(tmpdir):
    # When a rates db uses a real file, rates are remembered
    dbpath = str(tmpdir.join('foo.db'))
    db = RatesDB(dbpath)
    db.set_CAD_value(date(2008, 4, 20), 'USD', 1/0.996115)
    db = RatesDB(dbpath)
    assert_almost_equal(db.get_rate(date(2008, 4, 20), 'CAD', 'USD'), 0.996115)

def test_db_with_connection():
    # the supplied connection is used by the rates db.
    con = sqlite.connect(':memory:')
    db = RatesDB(con)
    try:
        con.execute("select * from rates where 1=2")
    except sqlite.OperationalError: # new db
        raise AssertionError()

def test_corrupt_db(tmpdir):
    dbpath = str(tmpdir.join('foo.db'))
    fh = open(dbpath, 'w')
    fh.write('corrupted')
    fh.close()
    db = RatesDB(dbpath) # no crash. deletes the old file and start a new db
    db.set_CAD_value(date(2008, 4, 20), 'USD', 42)
    db = RatesDB(dbpath)
    eq_(db.get_rate(date(2008, 4, 20), 'USD', 'CAD'), 42)

#--- Daily rate
def setup_daily_rate():
    USD.set_CAD_value(1/0.996115, date(2008, 4, 20))

def test_get_rate_with_daily_rate():
    # Getting the rate exactly as set_rate happened returns the same rate.
    setup_daily_rate()
    assert_almost_equal(CAD.value_in(USD, date(2008, 4, 20)), 0.996115)

def test_get_rate_different_currency():
    # Use fallback rates when necessary.
    setup_daily_rate()
    eq_(CAD.value_in(EUR, date(2008, 4, 20)), 1 / EUR.latest_rate)
    eq_(EUR.value_in(USD, date(2008, 4, 20)), EUR.latest_rate * 0.996115)

def test_get_rate_reverse():
    # It's possible to get the reverse value of a rate using the same data.
    setup_daily_rate()
    assert_almost_equal(USD.value_in(CAD, date(2008, 4, 20)), 1 / 0.996115)

def test_set_rate_twice():
    # When setting a rate for an index that already exists, the old rate is replaced by the new.
    setup_daily_rate()
    USD.set_CAD_value(1/42, date(2008, 4, 20))
    assert_almost_equal(CAD.value_in(USD, date(2008, 4, 20)), 42)

def test_set_rate_after_get():
    # When setting a rate after a get of the same rate, the rate cache is correctly updated.
    setup_daily_rate()
    CAD.value_in(USD, date(2008, 4, 20)) # value will be cached
    USD.set_CAD_value(1/42, date(2008, 4, 20))
    assert_almost_equal(CAD.value_in(USD, date(2008, 4, 20)), 42)

def test_set_rate_after_get_the_day_after():
    # When setting a rate, the cache for the whole currency is reset, or else we get old fallback
    # values for dates where the currency server returned no value.
    setup_daily_rate()
    CAD.value_in(USD, date(2008, 4, 21)) # value will be cached
    USD.set_CAD_value(1/42, date(2008, 4, 20))
    assert_almost_equal(CAD.value_in(USD, date(2008, 4, 21)), 42)

#--- Two daily rates
def setup_two_daily_rate():
    # Don't change the set order, it's important for the tests
    USD.set_CAD_value(1/0.997115, date(2008, 4, 25))
    USD.set_CAD_value(1/0.996115, date(2008, 4, 20))

def test_date_range_range():
    # USD.rates_date_range() returns the USD's limits.
    setup_two_daily_rate()
    eq_(USD.rates_date_range(), (date(2008, 4, 20), date(2008, 4, 25)))

def test_date_range_for_unfetched_currency():
    # If the curency is not in the DB, return None.
    setup_two_daily_rate()
    assert PLN.rates_date_range() is None

def test_seek_rate_middle():
    # A rate request with seek in the middle will return the lowest date.
    setup_two_daily_rate()
    eq_(USD.value_in(CAD, date(2008, 4, 24)), 1/0.996115)

def test_seek_rate_after():
    # Make sure that the *nearest* lowest rate is returned. Because the 25th have been set 
    # before the 20th, an order by clause is required in the seek SQL to make this test pass.
    setup_two_daily_rate()
    eq_(USD.value_in(CAD, date(2008, 4, 26)), 1/0.997115)

def test_seek_rate_before():
    # If there are no rate in the past, seek for a rate in the future.
    setup_two_daily_rate()
    eq_(USD.value_in(CAD, date(2008, 4, 19)), 1/0.996115)

#--- Rates of multiple currencies
def setup_rates_of_multiple_currencies():
    USD.set_CAD_value(1/0.996115, date(2008, 4, 20))
    EUR.set_CAD_value(1/0.633141, date(2008, 4, 20))

def test_get_rate_multiple_currencies():
    # Don't mix currency rates up.
    setup_rates_of_multiple_currencies()
    assert_almost_equal(CAD.value_in(USD, date(2008, 4, 20)), 0.996115)
    assert_almost_equal(CAD.value_in(EUR, date(2008, 4, 20)), 0.633141)

def test_get_rate_with_pivotal():
    # It's possible to get a rate by using 2 records.
    # if 1 CAD = 0.996115 USD and 1 CAD = 0.633141 then 0.996115 USD = 0.633141 then 1 USD = 0.633141 / 0.996115 EUR
    setup_rates_of_multiple_currencies()
    assert_almost_equal(USD.value_in(EUR, date(2008, 4, 20)), 0.633141 / 0.996115)

def test_get_rate_doesnt_exist():
    # Don't crash when trying to do pivotal calculation with non-existing currencies.
    setup_rates_of_multiple_currencies()
    eq_(USD.value_in(PLN, date(2008, 4, 20)), 1 / 0.996115 / PLN.latest_rate)

#--- Problems after connection
def get_problematic_db():
    class MockConnection(sqlite.Connection): # can't mock sqlite3.Connection's attribute, so we subclass it
        mocking = False
        def execute(self, *args, **kwargs):
            if self.mocking:
                raise sqlite.OperationalError()
            else:
                return sqlite.Connection.execute(self, *args, **kwargs)
    
    con = MockConnection(':memory:')
    db = RatesDB(con)
    con.mocking = True
    return db

def test_date_range_with_problematic_db():
    db = get_problematic_db()
    db.date_range('USD') # no crash

def test_get_rate_with_problematic_db():
    db = get_problematic_db()
    db.get_rate(date(2008, 4, 20), 'USD', 'CAD') # no crash

def test_set_rate_with_problematic_db():
    db = get_problematic_db()
    db.set_CAD_value(date(2008, 4, 20), 'USD', 42) # no crash

#--- DB that doesn't allow get_rate calls
def setup_db_raising_error_on_getrate():
    db = RatesDB()
    def mock_get_rate(*args, **kwargs):
        raise AssertionError()
    db.get_rate = mock_get_rate
    Currency.set_rates_db(db)

def test_currency_with_start_date():
    setup_db_raising_error_on_getrate()
    eq_(FOO.value_in(CAD, date(2009, 1, 11)), 2)

def test_currency_with_stop_date():
    setup_db_raising_error_on_getrate()
    eq_(BAR.value_in(CAD, date(2010, 1, 13)), 2)
