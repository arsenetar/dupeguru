===================================
:mod:`currency` - Manage currencies
===================================

This module facilitates currencies management. It exposes :class:`Currency` which lets you easily figure out their exchange value.

The ``Currency`` class
======================

.. class:: Currency(code=None, name=None)

    A ``Currency`` instance is created with either a 3-letter ISO code or with a full name. If it's present in the database, an instance will be returned. If not, ``ValueError`` is raised. The easiest way to access a currency instance, however, if by using module-level constants. For example::

        >>> from hscommon.currency import USD, EUR
        >>> from datetime import date
        >>> USD.value_in(EUR, date.today())
        0.6339119851386843

    Unless a :class:`currency.RatesDB` global instance is set through :meth:`Currency.set_rate_db` however, only fallback values will be used as exchange rates.

    .. staticmethod:: Currency.register(code, name, exponent=2, fallback_rate=1)

        Register a new currency in the currency list.

    .. staticmethod:: Currency.set_rates_db(db)

        Sets a new currency ``RatesDB`` instance to be used with all ``Currency`` instances.

    .. staticmethod:: Currency.set_rates_db()

        Returns the current ``RatesDB`` instance.

    .. method:: Currency.rates_date_range()

        Returns the range of date for which rates are available for this currency.

    .. method:: Currency.value_in(currency, date)

        Returns the value of this currency in terms of the other currency on the given date.

    .. method:: Currency.set_CAD_value(value, date)

        Sets currency's value in CAD on the given date.

The ``RatesDB`` class
=====================

.. class:: RatesDB(db_or_path=':memory:')

    A sqlite database that stores currency/date/value pairs, "value" being the value of the currency in CAD at the given date. Currencies are referenced by their 3-letter ISO code in the database and it its arguments (so ``currency_code`` arguments must be 3-letter strings).
    
    .. method:: RatesDB.date_range(currency_code)

        Returns a tuple ``(start_date, end_date)`` representing dates covered in the database for currency ``currency_code``. If there are gaps, they are not accounted for (subclasses that automatically update themselves are not supposed to introduce gaps in the db).

    .. method:: RatesDB.get_rate(date, currency1_code, currency2_code)

        Returns the exchange rate between currency1 and currency2 for date. The rate returned means '1 unit of currency1 is worth X units of currency2'. The rate of the nearest date that is smaller than 'date' is returned. If there is none, a seek for a rate with a higher date will be made.

    .. method:: RatesDB.set_CAD_value(date, currency_code, value)

        Sets the CAD value of ``currency_code`` at ``date`` to ``value`` in the database.
