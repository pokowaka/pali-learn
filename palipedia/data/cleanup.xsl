<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl = "http://www.w3.org/1999/XSL/Transform" version = "1.0">
    <xsl:template match = "/">
        <doc>
            <xsl:apply-templates select="/*"/>
        </doc>
    </xsl:template>

    <xsl:template match='p[@rend="bodytext"]'>
        <p>
            <xsl:apply-templates/>
        </p>
    </xsl:template>

    <xsl:template match='p[@rend="hangnum"]'>
        <xsl:choose>
            <xsl:when test="@n">
                <number>
                    <xsl:attribute name='nr'>
                        <xsl:value-of select="@n"/>
                    </xsl:attribute>
                </number>
            </xsl:when>
            <xsl:otherwise>
                <number>
                    <xsl:attribute name='nr'>
                        <xsl:value-of select="text()"/>
                    </xsl:attribute>
                </number>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match='p[@rend="unindented"]'>
        <p class="unindented">
            <xsl:apply-templates/>
        </p>
    </xsl:template>

    <xsl:template match='p[@rend="indent"]'>
        <p class="indent">
            <xsl:apply-templates/>
        </p>
    </xsl:template>

    <xsl:template match="note">
        <note>
            <xsl:apply-templates/>
        </note>
    </xsl:template>

    <xsl:template match='hi[@rend="bold"]'>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match='hi[@rend="paranum"]'>
        <number>
            <xsl:attribute name='nr'>
                <xsl:value-of select="text()"/>
            </xsl:attribute>
        </number>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:value-of select="."/>
    </xsl:template>

    <xsl:template match='p[@rend="centre"]'>
        <p class="centered">
            <xsl:apply-templates/>
        </p>
    </xsl:template>

    <xsl:template match='p[@rend="subsubhead"]'>
        <subsection>
            <xsl:attribute name='title'>
                <xsl:value-of select="text()"/>
            </xsl:attribute>
        </subsection>
    </xsl:template>

    <xsl:template match='hi[@rend="dot"]'>
    </xsl:template>

    <xsl:template match='p[@rend="book"]'>
        <book>
            <xsl:apply-templates/>
        </book>
    </xsl:template>

    <xsl:template match='p[@rend="chapter"]'>
        <chapter>
            <xsl:attribute name='title'>
                <xsl:value-of select="text()"/>
            </xsl:attribute>
        </chapter>
    </xsl:template>

    <xsl:template match='p[@rend="subhead"]'>
        <section>
            <xsl:attribute name='title'>
                <xsl:value-of select="text()"/>
            </xsl:attribute>
        </section>
    </xsl:template>

    <xsl:template match='p[@rend="nikaya"]'>
        <nikaya>
            <xsl:attribute name='title'>
                <xsl:value-of select="text()"/>
            </xsl:attribute>
        </nikaya>
    </xsl:template>

    <xsl:template match='p[@rend="title"]'>
        <!-- Seems to be unused -->
        <title>
            <xsl:apply-templates/>
        </title>
    </xsl:template>

    <xsl:template match='p[@rend="gatha1"]'>
        <verse idx='first'>
            <xsl:apply-templates/>
        </verse>
    </xsl:template>

    <xsl:template match='p[@rend="gatha2"]'>
        <verse>
            <xsl:apply-templates/>
        </verse>
    </xsl:template>

    <xsl:template match='p[@rend="gatha3"]'>
        <verse>
            <xsl:apply-templates/>
        </verse>
    </xsl:template>

    <xsl:template match='p[@rend="gathalast"]'>
        <verse idx="last">
            <xsl:apply-templates/>
        </verse>
    </xsl:template>

    <xsl:template match="pb">
        <pb>
            <xsl:attribute name='ed'>
                <xsl:value-of select="@ed"/>
            </xsl:attribute>
            <xsl:attribute name='n'>
                <xsl:value-of select="@n"/>
            </xsl:attribute>
        </pb>
    </xsl:template>

</xsl:stylesheet>
