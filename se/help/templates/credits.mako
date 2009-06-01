<%!
	title = 'Credits'
	selected_menu_item = 'Credits'
%>
<%inherit file="/base_dg.mako"/>
Below is the list of people who contributed, directly or indirectly to dupeGuru.

${self.credit('Virgil Dupras', 'Developer', "That's me, Hardcoded Software founder", 'www.hardcoded.net', 'hsoft@hardcoded.net')}

${self.credit('Jerome', 'Icon designer', "Icons in dupeGuru are from him")}

${self.credit('Python', 'Programming language', "The bestest of the bests", 'www.python.org')}

${self.credit('PyObjC', 'Python-to-Cocoa bridge', "Used for the Mac OS X version", 'pyobjc.sourceforge.net')}

${self.credit('Python for .NET', 'Python-to-.NET bridge', "Used for the Windows version", 'sourceforge.net/projects/pythonnet/')}

${self.credit('Sparkle', 'Auto-update library', "Used for the Mac OS X version", 'andymatuschak.org/pages/sparkle')}

${self.credit('You', 'dupeGuru user', "What would I do without you?")}
