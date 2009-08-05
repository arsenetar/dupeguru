# Created By: Virgil Dupras
# Created On: 2006/09/16
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from xml.dom import minidom
import tempfile
import os.path as op
import os
from StringIO import StringIO

from hsutil.files import FileOrPath

def output_column_xml(outfile, columns):
    """Creates a xml file outfile with the supplied columns.
    
    outfile can be a filename or a file object.
    columns is a list of 2 sized tuples (display,enabled)
    """
    doc = minidom.Document()
    root = doc.appendChild(doc.createElement('columns'))
    for display,enabled in columns:
        col_node = root.appendChild(doc.createElement('column'))
        col_node.setAttribute('display', display)
        col_node.setAttribute('enabled', {True:'y',False:'n'}[enabled])
    with FileOrPath(outfile, 'wb') as fp:
        doc.writexml(fp, '\t','\t','\n', encoding='utf-8')

def merge_css_into_xhtml(xhtml, css):
    with FileOrPath(xhtml, 'r+') as xhtml:
        with FileOrPath(css) as css:
            try:
                doc = minidom.parse(xhtml)
            except Exception:
                return False
            head = doc.getElementsByTagName('head')[0]
            links = head.getElementsByTagName('link')
            for link in links:
                if link.getAttribute('rel') == 'stylesheet':
                    head.removeChild(link)
            style = head.appendChild(doc.createElement('style'))
            style.setAttribute('type','text/css')
            style.appendChild(doc.createTextNode(css.read()))
            xhtml.truncate(0)
            doc.writexml(xhtml, '\t','\t','\n', encoding='utf-8')
            xhtml.seek(0)
    return True

def export_to_xhtml(xml, xslt, css, columns, cmd='xsltproc --path "%(folder)s" "%(xslt)s" "%(xml)s"'):
    folder = op.split(xml)[0]
    output_column_xml(op.join(folder,'columns.xml'),columns)
    html = StringIO()
    cmd = cmd % {'folder': folder, 'xslt': xslt, 'xml': xml}
    html.write(os.popen(cmd).read())
    html.seek(0)
    merge_css_into_xhtml(html,css)
    html.seek(0)
    html_path = op.join(folder,'export.htm')
    html_file = open(html_path,'w')
    html_file.write(html.read().encode('utf-8'))
    html_file.close()
    return html_path
