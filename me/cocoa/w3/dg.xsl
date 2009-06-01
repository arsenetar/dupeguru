<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output 
	method="xml"
	encoding="utf-8"
	doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
	doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
	indent="yes"/>

<xsl:template match="column">
	<xsl:if test="@enabled = 'y'">
		<th>
			<xsl:value-of select="@display"/>
		</th>
	</xsl:if>
</xsl:template>

<xsl:template match="file">
	<tr>
		<xsl:variable name="td_class">
			<xsl:if test="position() > 1">
		        <xsl:text>indented</xsl:text>
			</xsl:if>
		</xsl:variable>
		<xsl:variable name="file_node" select="."/>
		<xsl:for-each select="data">
			<xsl:variable name="data_pos" select="position()"/>
			<xsl:if test="document('columns.xml')/columns/column[$data_pos]/@enabled = 'y'">
				<td>
					<xsl:if test="position() = 1">
						<xsl:attribute name="class">
			            	<xsl:value-of select="$td_class"/>
			        	</xsl:attribute>
					</xsl:if>
					<xsl:value-of select="@value"/>
				</td>
			</xsl:if>
		</xsl:for-each>
		<!-- <xsl:for-each select="//results/column">
			<td>
				<xsl:variable name="attr_name">
					<xsl:text>attr_</xsl:text>
					<xsl:value-of select="@name"/>
				</xsl:variable>
				<xsl:value-of select="$file_node/@*[local-name(.) = $attr_name]"/>
			</td>
		</xsl:for-each> -->
	</tr>
</xsl:template>

<xsl:template match="group">
	<xsl:apply-templates select="file"/>
</xsl:template>

<xsl:template match="results">
	<html>
		<head>
			<title>dupeGuru Results</title>
			<link rel="stylesheet" href="hardcoded.css" type="text/css"/>
		</head>
		<body>
            <h1>dupeGuru Results</h1>
			<table>
				<tr>
					<xsl:apply-templates select="document('columns.xml')/columns/column"/>
				</tr>
				<xsl:apply-templates select="group"/>
			</table>
		</body>
	</html>
</xsl:template>

</xsl:stylesheet>