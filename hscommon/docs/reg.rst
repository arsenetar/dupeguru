========================================
:mod:`reg` - Manage app registration
========================================

.. module:: reg

.. class:: RegistrableApplication

    HS main application classes subclass this. It provides an easy interface for managing whether the app should be in demo mode or not.
    
    .. method:: _setup_as_registered()
    
        Virtual. This is called whenever the app is unlocked. This is the one place to put code that changes to UI to indicate that the app is unlocked.
    
    .. method:: validate_code(code, email)
    
        Validates ``code`` with email. If it's valid, it does nothing. Otherwise, it raises ``InvalidCodeError`` with a message indicating why it's invalid (wrong product, wrong code format, fields swapped).
    
    .. method:: set_registration(code, email)
    
        If ``code`` and ``email`` are valid, sets ``registered`` to True as well as ``registration_code`` and ``registration_email`` and then calls :meth:`_setup_as_registered`.

.. exception:: InvalidCodeError

    Raised during :meth:`RegistrableApplication.validate_code`.
