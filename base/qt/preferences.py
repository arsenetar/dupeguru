#!/usr/bin/env python
# Unit Name: preferences
# Created By: Virgil Dupras
# Created On: 2009-05-03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from PyQt4.QtCore import QSettings, QVariant

from hsutil.misc import tryint

def variant_to_py(v):
    value = None
    ok = False
    t = v.type()
    if t == QVariant.String:
        value = unicode(v.toString())
        ok = True # anyway
        # might be bool or int, try them
        if v == 'true':
            value = True
        elif value == 'false':
            value = False
        else:
            value = tryint(value, value)
    elif t == QVariant.Int:
        value, ok = v.toInt()
    elif t == QVariant.Bool:
        value, ok = v.toBool(), True
    elif t in (QVariant.List, QVariant.StringList):
        value, ok = map(variant_to_py, v.toList()), True
    if not ok:
        raise TypeError()
    return value    

class Preferences(object):
    # (width, is_visible)
    COLUMNS_DEFAULT_ATTRS = []
    
    def __init__(self):
        self.reset()
        self.reset_columns()
    
    def _load_specific(self, settings, get):
        # load prefs specific to the dg edition
        pass
    
    def load(self):
        self.reset()
        settings = QSettings()
        def get(name, default):
            if settings.contains(name):
                return variant_to_py(settings.value(name))
            else:
                return default
        
        self.filter_hardness = get('FilterHardness', self.filter_hardness)
        self.mix_file_kind = get('MixFileKind', self.mix_file_kind)
        self.use_regexp = get('UseRegexp', self.use_regexp)
        self.remove_empty_folders = get('RemoveEmptyFolders', self.remove_empty_folders)
        self.destination_type = get('DestinationType', self.destination_type)
        widths = get('ColumnsWidth', self.columns_width)
        # only set nonzero values
        for index, width in enumerate(widths[:len(self.columns_width)]):
            if width > 0:
                self.columns_width[index] = width
        self.columns_visible = get('ColumnsVisible', self.columns_visible)
        self.registration_code = get('RegistrationCode', self.registration_code)
        self.registration_email = get('RegistrationEmail', self.registration_email)
        self._load_specific(settings, get)
    
    def _reset_specific(self):
        # reset prefs specific to the dg edition
        pass
    
    def reset(self):
        self.filter_hardness = 95
        self.mix_file_kind = True
        self.use_regexp = False
        self.remove_empty_folders = False
        self.destination_type = 1
        self.registration_code = ''
        self.registration_email = ''
        self._reset_specific()
    
    def reset_columns(self):
        self.columns_width = [width for width, _ in self.COLUMNS_DEFAULT_ATTRS]
        self.columns_visible = [visible for _, visible in self.COLUMNS_DEFAULT_ATTRS]
    
    def _save_specific(self, settings, set_):
        # save prefs specific to the dg edition
        pass
    
    def save(self):
        settings = QSettings()
        def set_(name, value):
            settings.setValue(name, QVariant(value))
        
        set_('FilterHardness', self.filter_hardness)
        set_('MixFileKind', self.mix_file_kind)
        set_('UseRegexp', self.use_regexp)
        set_('RemoveEmptyFolders', self.remove_empty_folders)
        set_('DestinationType', self.destination_type)
        set_('ColumnsWidth', self.columns_width)
        set_('ColumnsVisible', self.columns_visible)
        set_('RegistrationCode', self.registration_code)
        set_('RegistrationEmail', self.registration_email)
        self._save_specific(settings, set_)
    
