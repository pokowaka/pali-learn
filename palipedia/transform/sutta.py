from lxml import etree
import re
import palipedia.transform.xml as xml

# Sutta specific transformers.


def normalize_chapter(tree):
    '''<chapter> --> <chapter nr='xx' title='yy'>'''
    for node in tree.xpath('//chapter'):
        if len(node) > 0:
            raise "Has kids, cannot clean!"
        m = re.search('(.*)\.(.*)', node.text)
        if not m:
            node.attrib['title'] = node.text
            node.text = None
        else:
            node.attrib['nr'] = m.group(1).strip()
            node.attrib['title'] = m.group(2).strip()
            node.text = None


def merge_verses(tree):
    tags = list(tree.xpath('//gatha'))
    tags.reverse()
    for node, nxt in xml.pairwise(tags):
        # neighbors?
        if (nxt is node.getprevious() and
                (node.attrib['type'].strip() != '1')):
            xml.merge(nxt, node)
            node.getparent().remove(node)
