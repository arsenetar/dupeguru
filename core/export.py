# Created By: Virgil Dupras
# Created On: 2006/09/16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import tempfile
import os.path as op
from tempfile import mkdtemp

# Yes, this is a very low-tech solution, but at least it doesn't have all these annoying dependency
# and resource problems.

MAIN_TEMPLATE = u"""
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Strict//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
	<title>dupeGuru Results</title>
	<style type="text/css">
BODY
{
	background-color:white;
}

BODY,A,P,UL,TABLE,TR,TD
{
	font-family:Tahoma,Arial,sans-serif;
	font-size:10pt;
	color: #4477AA;
}

TABLE
{
	background-color: #225588;
	margin-left: auto;
  	margin-right: auto;
	width: 90%;
}

TR 
{
    background-color: white;
}

TH 
{ 
	font-weight: bold; 
	color: black;
	background-color: #C8D6E5;
}

TH TD 
{
    color:black;
}

TD 
{
    padding-left: 2pt;
}

TD.rightelem
{
	text-align:right;
	/*padding-left:0pt;*/
	padding-right: 2pt;
	width: 17%;
}

TD.indented
{
    padding-left: 12pt;
}

H1
{
	font-family:&quot;Courier New&quot;,monospace;
	color:#6699CC;
    font-size:18pt; 
	color:#6da500;
	border-color: #70A0CF;
	border-width: 1pt;
	border-style: solid;
	margin-top:   16pt;
	margin-left:  5%;
	margin-right: 5%;
	padding-top:  2pt;
	padding-bottom:2pt;
	text-align:   center;
}
</style>
</head>
<body>
<h1>dupeGuru Results</h1>
<table>
<tr>$colheaders</tr>
$rows
</table>
</body>
</html>
"""

COLHEADERS_TEMPLATE = u"<th>{name}</th>"

ROW_TEMPLATE = u"""
<tr>
    <td class="{indented}">{filename}</td>{cells}
</tr>
"""

CELL_TEMPLATE = u"""<td>{value}</td>"""

def export_to_xhtml(colnames, rows):
    # a row is a list of values with the first value being a flag indicating if the row should be indented
    if rows:
        assert len(rows[0]) == len(colnames) + 1 # + 1 is for the "indented" flag
    colheaders = u''.join(COLHEADERS_TEMPLATE.format(name=name) for name in colnames)
    rendered_rows = []
    for row in rows:
        # [2:] is to remove the indented flag + filename
        indented = u'indented' if row[0] else u''
        filename = row[1]
        cells = u''.join(CELL_TEMPLATE.format(value=value) for value in row[2:])
        rendered_rows.append(ROW_TEMPLATE.format(indented=indented, filename=filename, cells=cells))
    rendered_rows = u''.join(rendered_rows)
    # The main template can't use format because the css code uses {}
    content = MAIN_TEMPLATE.replace('$colheaders', colheaders).replace('$rows', rendered_rows)
    folder = mkdtemp()
    destpath = op.join(folder, u'export.htm')
    fp = open(destpath, 'w')
    fp.write(content.encode('utf-8'))
    fp.close()
    return destpath
