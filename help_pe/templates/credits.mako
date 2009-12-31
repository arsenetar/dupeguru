## -*- coding: utf-8 -*-
<%!
	title = 'Credits'
	selected_menu_item = 'Credits'
%>
<%inherit file="/base_dg.mako"/>
Below is the list of people who contributed, directly or indirectly to dupeGuru.

${self.credit('Virgil Dupras', 'Developer', "That's me, Hardcoded Software founder", 'www.hardcoded.net', 'hsoft@hardcoded.net')}

${self.credit(u'Jérôme Cantin', u'Icon designer', u"Icons in dupeGuru are from him")}

${self.credit('Python', 'Programming language', "The bestest of the bests", 'www.python.org')}

${self.credit('PyObjC', 'Python-to-Cocoa bridge', "Used for the Mac OS X version", 'pyobjc.sourceforge.net')}

${self.credit('PyQt', 'Python-to-Qt bridge', "Used for the Windows version", 'www.riverbankcomputing.co.uk')}

${self.credit('Qt', 'GUI Toolkit', "Used for the Windows version", 'www.qtsoftware.com')}

${self.credit('Sparkle', 'Auto-update library', "Used for the Mac OS X version", 'andymatuschak.org/pages/sparkle')}

${self.credit('Python Imaging Library', 'Picture analyzer', "Used for the Windows version", 'www.pythonware.com/products/pil/')}

${self.credit('You', 'dupeGuru user', "What would I do without you?")}
