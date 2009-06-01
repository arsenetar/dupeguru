<%inherit file="/base_help.mako"/>
${next.body()}

<%def name="menu()"><%
self.menuitem('intro.htm', 'Introduction', 'Introduction to dupeGuru')
self.menuitem('quick_start.htm', 'Quick Start', 'Quickly get into the action')
self.menuitem('directories.htm', 'Directories', 'Managing dupeGuru directories')
self.menuitem('preferences.htm', 'Preferences', 'Setting dupeGuru preferences')
self.menuitem('results.htm', 'Results', 'Time to delete these duplicates!')
self.menuitem('power_marker.htm', 'Power Marker', 'Take control of your duplicates')
self.menuitem('faq.htm', 'F.A.Q.', 'Frequently Asked Questions')
self.menuitem('versions.htm', 'Version History', 'Changes dupeGuru went through')
self.menuitem('credits.htm', 'Credits', 'People who contributed to dupeGuru')
%></%def>