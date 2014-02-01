# Created By: Virgil Dupras
# Created On: 2008-04-20
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

"""This module facilitates currencies management. It exposes :class:`Currency` which lets you
easily figure out their exchange value.
"""

import os
from datetime import datetime, date, timedelta
import logging
import sqlite3 as sqlite
import threading
from queue import Queue, Empty

from .path import Path
from .util import iterdaterange

class Currency:
    """Represents a currency and allow easy exchange rate lookups.
    
    A ``Currency`` instance is created with either a 3-letter ISO code or with a full name. If it's
    present in the database, an instance will be returned. If not, ``ValueError`` is raised. The
    easiest way to access a currency instance, however, if by using module-level constants. For
    example::

        >>> from hscommon.currency import USD, EUR
        >>> from datetime import date
        >>> USD.value_in(EUR, date.today())
        0.6339119851386843

    Unless a :class:`RatesDB` global instance is set through :meth:`Currency.set_rate_db` however,
    only fallback values will be used as exchange rates.
    """
    all = []
    by_code = {}
    by_name = {}
    rates_db = None

    def __new__(cls, code=None, name=None):
        """Returns the currency with the given code."""
        assert (code is None and name is not None) or (code is not None and name is None)
        if code is not None:
            try:
                return cls.by_code[code]
            except KeyError:
                raise ValueError('Unknown currency code: %r' % code)
        else:
            try:
                return cls.by_name[name]
            except KeyError:
                raise ValueError('Unknown currency name: %r' % name)

    def __getnewargs__(self):
        return (self.code,)
 
    def __getstate__(self):
        return None
  
    def __setstate__(self, state):
        pass

    def __repr__(self):
        return '<Currency %s>' % self.code

    @staticmethod
    def register(code, name, exponent=2, start_date=None, start_rate=1, stop_date=None, latest_rate=1):
        """Registers a new currency and returns it."""
        assert code not in Currency.by_code
        assert name not in Currency.by_name
        currency = object.__new__(Currency)
        currency.code = code
        currency.name = name
        currency.exponent = exponent
        currency.start_date = start_date
        currency.start_rate = start_rate
        currency.stop_date = stop_date
        currency.latest_rate = latest_rate
        Currency.by_code[code] = currency
        Currency.by_name[name] = currency
        Currency.all.append(currency)
        return currency

    @staticmethod
    def set_rates_db(db):
        """Sets a new currency ``RatesDB`` instance to be used with all ``Currency`` instances.
        """
        Currency.rates_db = db

    @staticmethod
    def get_rates_db():
        """Returns the current ``RatesDB`` instance.
        """
        if Currency.rates_db is None:
            Currency.rates_db = RatesDB() # Make sure we always have some db to work with
        return Currency.rates_db

    def rates_date_range(self):
        """Returns the range of date for which rates are available for this currency."""
        return self.get_rates_db().date_range(self.code)

    def value_in(self, currency, date):
        """Returns the value of this currency in terms of the other currency on the given date."""
        if self.start_date is not None and date < self.start_date:
            return self.start_rate
        elif self.stop_date is not None and date > self.stop_date:
            return self.latest_rate
        else:
            return self.get_rates_db().get_rate(date, self.code, currency.code)
    
    def set_CAD_value(self, value, date):
        """Sets the currency's value in CAD on the given date."""
        self.get_rates_db().set_CAD_value(date, self.code, value)


BUILTIN_CURRENCIES = {
# In order we want to list them
Currency.register('USD', 'U.S. dollar',
    start_date=date(1998, 1, 2), start_rate=1.425, latest_rate=1.0128),
Currency.register('EUR', 'European Euro',
    start_date=date(1999, 1, 4), start_rate=1.8123, latest_rate=1.3298),
Currency.register('GBP', 'U.K. pound sterling',
    start_date=date(1998, 1, 2), start_rate=2.3397, latest_rate=1.5349),
Currency.register('CAD', 'Canadian dollar',
    latest_rate=1),
Currency.register('AUD', 'Australian dollar',
    start_date=date(1998, 1, 2), start_rate=0.9267, latest_rate=0.9336),
Currency.register('JPY', 'Japanese yen',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.01076, latest_rate=0.01076),
Currency.register('INR', 'Indian rupee',
    start_date=date(1998, 1, 2), start_rate=0.03627, latest_rate=0.02273),
Currency.register('NZD', 'New Zealand dollar',
    start_date=date(1998, 1, 2), start_rate=0.8225, latest_rate=0.7257),
Currency.register('CHF', 'Swiss franc',
    start_date=date(1998, 1, 2), start_rate=0.9717, latest_rate=0.9273),
Currency.register('ZAR', 'South African rand',
    start_date=date(1998, 1, 2), start_rate=0.292, latest_rate=0.1353),
# The rest, alphabetical
Currency.register('AED', 'U.A.E. dirham',
    start_date=date(2007, 9, 4), start_rate=0.2858, latest_rate=0.2757),
Currency.register('ANG', 'Neth. Antilles florin',
    start_date=date(1998, 1, 2), start_rate=0.7961, latest_rate=0.5722),
Currency.register('ARS', 'Argentine peso',
    start_date=date(1998, 1, 2), start_rate=1.4259, latest_rate=0.2589),
Currency.register('ATS', 'Austrian schilling',
    start_date=date(1998, 1, 2), start_rate=0.1123, stop_date=date(2001, 12, 31), latest_rate=0.10309), # obsolete (euro)
Currency.register('BBD', 'Barbadian dollar',
    start_date=date(2010, 4, 30), start_rate=0.5003, latest_rate=0.5003),
Currency.register('BEF', 'Belgian franc',
    start_date=date(1998, 1, 2), start_rate=0.03832, stop_date=date(2001, 12, 31), latest_rate=0.03516), # obsolete (euro)
Currency.register('BHD', 'Bahraini dinar',
    exponent=3, start_date=date(2008, 11, 8), start_rate=3.1518, latest_rate=2.6603),
Currency.register('BRL', 'Brazilian real',
    start_date=date(1998, 1, 2), start_rate=1.2707, latest_rate=0.5741),
Currency.register('BSD', 'Bahamian dollar',
    start_date=date(1998, 1, 2), start_rate=1.425, latest_rate=1.0128),
Currency.register('CLP', 'Chilean peso',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.003236, latest_rate=0.001923),
Currency.register('CNY', 'Chinese renminbi',
    start_date=date(1998, 1, 2), start_rate=0.1721, latest_rate=0.1484),
Currency.register('COP', 'Colombian peso',
    start_date=date(1998, 1, 2), start_rate=0.00109, latest_rate=0.000513),
Currency.register('CZK', 'Czech Republic koruna',
    start_date=date(1998, 2, 2), start_rate=0.04154, latest_rate=0.05202),
Currency.register('DEM', 'German deutsche mark',
    start_date=date(1998, 1, 2), start_rate=0.7904, stop_date=date(2001, 12, 31), latest_rate=0.7253), # obsolete (euro)
Currency.register('DKK', 'Danish krone',
    start_date=date(1998, 1, 2), start_rate=0.2075, latest_rate=0.1785),
Currency.register('EGP', 'Egyptian Pound',
    start_date=date(2008, 11, 27), start_rate=0.2232, latest_rate=0.1805),
Currency.register('ESP', 'Spanish peseta',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.009334, stop_date=date(2001, 12, 31), latest_rate=0.008526), # obsolete (euro)
Currency.register('FIM', 'Finnish markka',
    start_date=date(1998, 1, 2), start_rate=0.2611, stop_date=date(2001, 12, 31), latest_rate=0.2386), # obsolete (euro)
Currency.register('FJD', 'Fiji dollar',
    start_date=date(1998, 1, 2), start_rate=0.9198, latest_rate=0.5235),
Currency.register('FRF', 'French franc',
    start_date=date(1998, 1, 2), start_rate=0.2362, stop_date=date(2001, 12, 31), latest_rate=0.2163), # obsolete (euro)
Currency.register('GHC', 'Ghanaian cedi (old)',
    start_date=date(1998, 1, 2), start_rate=0.00063, stop_date=date(2007, 6, 29), latest_rate=0.000115), # obsolete
Currency.register('GHS', 'Ghanaian cedi',
    start_date=date(2007, 7, 3), start_rate=1.1397, latest_rate=0.7134),
Currency.register('GRD', 'Greek drachma',
    start_date=date(1998, 1, 2), start_rate=0.005, stop_date=date(2001, 12, 31), latest_rate=0.004163), # obsolete (euro)
Currency.register('GTQ', 'Guatemalan quetzal',
    start_date=date(2004, 12, 21), start_rate=0.15762, latest_rate=0.1264),
Currency.register('HKD', 'Hong Kong dollar',
    start_date=date(1998, 1, 2), start_rate=0.1838, latest_rate=0.130385),
Currency.register('HNL', 'Honduran lempira',
    start_date=date(1998, 1, 2), start_rate=0.108, latest_rate=0.0536),
Currency.register('HRK', 'Croatian kuna',
    start_date=date(2002, 3, 1), start_rate=0.1863, latest_rate=0.1837),
Currency.register('HUF', 'Hungarian forint',
    start_date=date(1998, 2, 2), start_rate=0.007003, latest_rate=0.00493),
Currency.register('IDR', 'Indonesian rupiah',
    start_date=date(1998, 2, 2), start_rate=0.000145, latest_rate=0.000112),
Currency.register('IEP', 'Irish pound',
    start_date=date(1998, 1, 2), start_rate=2.0235, stop_date=date(2001, 12, 31), latest_rate=1.8012), # obsolete (euro)
Currency.register('ILS', 'Israeli new shekel',
    start_date=date(1998, 1, 2), start_rate=0.4021, latest_rate=0.2706),
Currency.register('ISK', 'Icelandic krona',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.01962, latest_rate=0.00782),
Currency.register('ITL', 'Italian lira',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.000804, stop_date=date(2001, 12, 31), latest_rate=0.000733), # obsolete (euro)
Currency.register('JMD', 'Jamaican dollar',
    start_date=date(2001, 6, 25), start_rate=0.03341, latest_rate=0.01145),
Currency.register('KRW', 'South Korean won',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.000841, latest_rate=0.000905),
Currency.register('LKR', 'Sri Lanka rupee',
    start_date=date(1998, 1, 2), start_rate=0.02304, latest_rate=0.0089),
Currency.register('LTL', 'Lithuanian litas',
    start_date=date(2010, 4, 29), start_rate=0.384, latest_rate=0.384),
Currency.register('LVL', 'Latvian lats',
    start_date=date(2011, 2, 6), start_rate=1.9136, latest_rate=1.9136),
Currency.register('MAD', 'Moroccan dirham',
    start_date=date(1998, 1, 2), start_rate=0.1461, latest_rate=0.1195),
Currency.register('MMK', 'Myanmar (Burma) kyat',
    start_date=date(1998, 1, 2), start_rate=0.226, latest_rate=0.1793),
Currency.register('MXN', 'Mexican peso',
    start_date=date(1998, 1, 2), start_rate=0.1769, latest_rate=0.08156),
Currency.register('MYR', 'Malaysian ringgit',
    start_date=date(1998, 1, 2), start_rate=0.3594, latest_rate=0.3149),
# MZN in not supported in any of my sources, so I'm just creating it with a fixed rate.
Currency.register('MZN', 'Mozambican metical',
    start_date=date(2011, 2, 6), start_rate=0.03, stop_date=date(2011, 2, 5), latest_rate=0.03),
Currency.register('NIO', 'Nicaraguan córdoba',
    start_date=date(2011, 10, 12), start_rate=0.0448, latest_rate=0.0448),
Currency.register('NLG', 'Netherlands guilder',
    start_date=date(1998, 1, 2), start_rate=0.7013, stop_date=date(2001, 12, 31), latest_rate=0.6437), # obsolete (euro)
Currency.register('NOK', 'Norwegian krone',
    start_date=date(1998, 1, 2), start_rate=0.1934, latest_rate=0.1689),
Currency.register('PAB', 'Panamanian balboa',
    start_date=date(1998, 1, 2), start_rate=1.425, latest_rate=1.0128),
Currency.register('PEN', 'Peruvian new sol',
    start_date=date(1998, 1, 2), start_rate=0.5234, latest_rate=0.3558),
Currency.register('PHP', 'Philippine peso',
    start_date=date(1998, 1, 2), start_rate=0.0345, latest_rate=0.02262),
Currency.register('PKR', 'Pakistan rupee',
    start_date=date(1998, 1, 2), start_rate=0.03238, latest_rate=0.01206),
Currency.register('PLN', 'Polish zloty',
    start_date=date(1998, 2, 2), start_rate=0.4108, latest_rate=0.3382),
Currency.register('PTE', 'Portuguese escudo',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.007726, stop_date=date(2001, 12, 31), latest_rate=0.007076), # obsolete (euro)
Currency.register('RON', 'Romanian new leu',
    start_date=date(2007, 9, 4), start_rate=0.4314, latest_rate=0.3215),
Currency.register('RSD', 'Serbian dinar',
    start_date=date(2007, 9, 4), start_rate=0.0179, latest_rate=0.01338),
Currency.register('RUB', 'Russian rouble',
    start_date=date(1998, 1, 2), start_rate=0.2375, latest_rate=0.03443),
Currency.register('SAR', 'Saudi riyal',
    start_date=date(2012, 9, 13), start_rate=0.26, latest_rate=0.26),
Currency.register('SEK', 'Swedish krona',
    start_date=date(1998, 1, 2), start_rate=0.1787, latest_rate=0.1378),
Currency.register('SGD', 'Singapore dollar',
    start_date=date(1998, 1, 2), start_rate=0.84, latest_rate=0.7358),
Currency.register('SIT', 'Slovenian tolar',
    start_date=date(2002, 3, 1), start_rate=0.006174, stop_date=date(2006, 12, 29), latest_rate=0.006419), # obsolete (euro)
Currency.register('SKK', 'Slovak koruna',
    start_date=date(2002, 3, 1), start_rate=0.03308, stop_date=date(2008, 12, 31), latest_rate=0.05661), # obsolete (euro)
Currency.register('THB', 'Thai baht',
    start_date=date(1998, 1, 2), start_rate=0.0296, latest_rate=0.03134),
Currency.register('TND', 'Tunisian dinar',
    exponent=3, start_date=date(1998, 1, 2), start_rate=1.2372, latest_rate=0.7037),
Currency.register('TRL', 'Turkish lira',
    exponent=0, start_date=date(1998, 1, 2), start_rate=7.0e-06, stop_date=date(2004, 12, 31), latest_rate=8.925e-07), # obsolete
Currency.register('TWD', 'Taiwanese new dollar',
    start_date=date(1998, 1, 2), start_rate=0.04338, latest_rate=0.03218),
Currency.register('UAH', 'Ukrainian hryvnia',
    start_date=date(2010, 4, 29), start_rate=0.1266, latest_rate=0.1266),
Currency.register('VEB', 'Venezuelan bolivar',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.002827, stop_date=date(2007, 12, 31), latest_rate=0.00046), # obsolete
Currency.register('VEF', 'Venezuelan bolivar fuerte',
    start_date=date(2008, 1, 2), start_rate=0.4623, latest_rate=0.2358),
Currency.register('VND', 'Vietnamese dong',
    start_date=date(2004, 1, 1), start_rate=8.2e-05, latest_rate=5.3e-05),
Currency.register('XAF', 'CFA franc',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.002362, latest_rate=0.002027),
Currency.register('XCD', 'East Caribbean dollar',
    start_date=date(1998, 1, 2), start_rate=0.5278, latest_rate=0.3793),
Currency.register('XPF', 'CFP franc',
    exponent=0, start_date=date(1998, 1, 2), start_rate=0.01299, latest_rate=0.01114),
}
BUILTIN_CURRENCY_CODES = {c.code for c in BUILTIN_CURRENCIES}

# For legacy purpose, we need to maintain these global variables
CAD = Currency(code='CAD')
USD = Currency(code='USD')
EUR = Currency(code='EUR')

class CurrencyNotSupportedException(Exception):
    """The current exchange rate provider doesn't support the requested currency."""

class RateProviderUnavailable(Exception):
    """The rate provider is temporarily unavailable."""

def date2str(date):
    return '%d%02d%02d' % (date.year, date.month, date.day)

class RatesDB:
    """Stores exchange rates for currencies.
    
    The currencies are identified with ISO 4217 code (USD, CAD, EUR, etc.).
    The rates are represented as float and represent the value of the currency in CAD.
    """
    def __init__(self, db_or_path=':memory:', async=True):
        self._cache = {} # {(date, currency): CAD value
        self.db_or_path = db_or_path
        if isinstance(db_or_path, (str, Path)):
            self.con = sqlite.connect(str(db_or_path))
        else:
            self.con = db_or_path
        self._execute("select * from rates where 1=2")
        self._rate_providers = []
        self.async = async
        self._fetched_values = Queue()
        self._fetched_ranges = {} # a currency --> (start, end) map
    
    def _execute(self, *args, **kwargs):
        def create_tables():
            # date is stored as a TEXT YYYYMMDD
            sql = "create table rates(date TEXT, currency TEXT, rate REAL NOT NULL)"
            self.con.execute(sql)
            sql = "create unique index idx_rate on rates (date, currency)"
            self.con.execute(sql)
        
        try:
            return self.con.execute(*args, **kwargs)
        except sqlite.OperationalError: # new db, or other problems
            try:
                create_tables()
            except Exception:
                logging.warning("Messy problems with the currency db, starting anew with a memory db")
                self.con = sqlite.connect(':memory:')
                create_tables()
        except sqlite.DatabaseError: # corrupt db
            logging.warning("Corrupt currency database at {0}. Starting over.".format(repr(self.db_or_path)))
            if isinstance(self.db_or_path, (str, Path)):
                self.con.close()
                os.remove(str(self.db_or_path))
                self.con = sqlite.connect(str(self.db_or_path))
            else:
                logging.warning("Can't re-use the file, using a memory table")
                self.con = sqlite.connect(':memory:')
            create_tables()
        return self.con.execute(*args, **kwargs) # try again
    
    def _seek_value_in_CAD(self, str_date, currency_code):
        if currency_code == 'CAD':
            return 1
        def seek(date_op, desc):
            sql = "select rate from rates where date %s ? and currency = ? order by date %s limit 1" % (date_op, desc)
            cur = self._execute(sql, [str_date, currency_code])
            row = cur.fetchone()
            if row:
                return row[0]
        return seek('<=', 'desc') or seek('>=', '') or Currency(currency_code).latest_rate
    
    def _ensure_filled(self, date_start, date_end, currency_code):
        """Make sure that the cache contains *something* for each of the dates in the range.
        
        Sometimes, our provider doesn't return us the range we sought. When it does, it usually
        means that it never will and to avoid repeatedly querying those ranges forever, we have to
        fill them. We use the closest rate for this.
        """
        # We don't want to fill today, because we want to repeatedly fetch that one until the
        # provider gives it to us.
        if date_end >= date.today():
            date_end = date.today() - timedelta(1)
        sql = "select rate from rates where date = ? and currency = ?"
        for curdate in iterdaterange(date_start, date_end):
            cur = self._execute(sql, [date2str(curdate), currency_code])
            if cur.fetchone() is None:
                nearby_rate = self._seek_value_in_CAD(date2str(curdate), currency_code)
                self.set_CAD_value(curdate, currency_code, nearby_rate)
                logging.debug("Filled currency void for %s at %s (value: %2.2f)", currency_code, curdate, nearby_rate)
                
    def _save_fetched_rates(self):
        while True:
            try:
                rates, currency, fetch_start, fetch_end = self._fetched_values.get_nowait()
                logging.debug("Saving %d rates for the currency %s", len(rates), currency)
                for rate_date, rate in rates:
                    logging.debug("Saving rate %2.2f for %s", rate, rate_date)
                    self.set_CAD_value(rate_date, currency, rate)
                self._ensure_filled(fetch_start, fetch_end, currency)
                logging.debug("Finished saving rates for currency %s", currency)
            except Empty:
                break
    
    def clear_cache(self):
        self._cache = {}
    
    def date_range(self, currency_code):
        """Returns (start, end) of the cached rates for currency.
        
        Returns a tuple ``(start_date, end_date)`` representing dates covered in the database for
        currency ``currency_code``. If there are gaps, they are not accounted for (subclasses that
        automatically update themselves are not supposed to introduce gaps in the db).
        """
        sql = "select min(date), max(date) from rates where currency = '%s'" % currency_code
        cur = self._execute(sql)
        start, end = cur.fetchone()
        if start and end:
            convert = lambda s: datetime.strptime(s, '%Y%m%d').date()
            return convert(start), convert(end)
        else:
            return None
    
    def get_rate(self, date, currency1_code, currency2_code):
        """Returns the exchange rate between currency1 and currency2 for date.
        
        The rate returned means '1 unit of currency1 is worth X units of currency2'.
        The rate of the nearest date that is smaller than 'date' is returned. If
        there is none, a seek for a rate with a higher date will be made.
        """
        # We want to check self._fetched_values for rates to add.
        if not self._fetched_values.empty():
            self._save_fetched_rates()
        # This method is a bottleneck and has been optimized for speed.
        value1 = None
        value2 = None
        if currency1_code == 'CAD':
            value1 = 1
        else:
            value1 = self._cache.get((date, currency1_code))
        if currency2_code == 'CAD':
            value2 = 1
        else:
            value2 = self._cache.get((date, currency2_code))
        if value1 is None or value2 is None:
            str_date = date2str(date)
            if value1 is None:
                value1 = self._seek_value_in_CAD(str_date, currency1_code)
                self._cache[(date, currency1_code)] = value1
            if value2 is None:
                value2 = self._seek_value_in_CAD(str_date, currency2_code)
                self._cache[(date, currency2_code)] = value2
        return value1 / value2
    
    def set_CAD_value(self, date, currency_code, value):
        """Sets the daily value in CAD for currency at date"""
        # we must clear the whole cache because there might be other dates affected by this change
        # (dates when the currency server has no rates).
        self.clear_cache()
        str_date = date2str(date)
        sql = "replace into rates(date, currency, rate) values(?, ?, ?)"
        self._execute(sql, [str_date, currency_code, value])
        self.con.commit()
    
    def register_rate_provider(self, rate_provider):
        """Adds `rate_provider` to the list of providers supported by this DB.
        
        A provider if a function(currency, start_date, end_date) that returns a list of
        (rate_date, float_rate) as a result. This function will be called asyncronously, so it's ok
        if it takes a long time to return.
        
        The rates returned must be the value of 1 `currency` in CAD (Canadian Dollars) at the
        specified date.
        
        The provider can be asked for any currency. If it doesn't support it, it has to raise
        CurrencyNotSupportedException.
        
        If we support the currency but that there is no rate available for the specified range,
        simply return an empty list or None.
        """
        self._rate_providers.append(rate_provider)
    
    def ensure_rates(self, start_date, currencies):
        """Ensures that the DB has all the rates it needs for 'currencies' between 'start_date' and today
        
        If there is any rate missing, a request will be made to the currency server. The requests
        are made asynchronously.
        """
        def do():
            for currency, fetch_start, fetch_end in currencies_and_range:
                logging.debug("Fetching rates for %s for date range %s to %s", currency, fetch_start, fetch_end)
                for rate_provider in self._rate_providers:
                    try:
                        values = rate_provider(currency, fetch_start, fetch_end)
                    except CurrencyNotSupportedException:
                        continue
                    except RateProviderUnavailable:
                        logging.debug("Fetching failed due to temporary problems.")
                        break
                    else:
                        if not values:
                            # We didn't get any value from the server, which means that we asked for
                            # rates that couldn't be delivered. Still, we report empty values so
                            # that the cache can correctly remember this unavailability so that we
                            # don't repeatedly fetch those ranges.
                            values = []
                        self._fetched_values.put((values, currency, fetch_start, fetch_end))
                        logging.debug("Fetching successful!")
                        break
                else:
                    logging.debug("Fetching failed!")
        
        currencies_and_range = []
        for currency in currencies:
            if currency == 'CAD':
                continue
            try:
                cached_range = self._fetched_ranges[currency]
            except KeyError:
                cached_range = self.date_range(currency)
            range_start = start_date
            # Don't try to fetch today's rate, it's never there and results in useless server
            # hitting.
            range_end = date.today() - timedelta(1)
            if cached_range is not None:
                cached_start, cached_end = cached_range
                if range_start >= cached_start:
                    # Make a forward fetch
                    range_start = cached_end + timedelta(days=1)
                else:
                    # Make a backward fetch
                    range_end = cached_start - timedelta(days=1)
            # We don't want to fetch ranges that are too big. It can cause various problems, such
            # as hangs. We prefer to take smaller bites.
            if (range_end - range_start).days > 30:
                range_start = range_end - timedelta(days=30)
            if range_start <= range_end:
                currencies_and_range.append((currency, range_start, range_end))
            self._fetched_ranges[currency] = (start_date, date.today())
        if self.async:
            threading.Thread(target=do).start()
        else:
            do()
    
