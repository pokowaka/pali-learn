from lxml import etree
import re
import palipedia.transform.xml as xml

# Sutta specific transformers.
def is_toc(node):
    return not is_text(node)

def is_text(node):
    return node.tag == 'tree' and len(node) == 1 and node[0].tag == 'text'


def merge_verses(tree):
    tags = list(tree.xpath('//gatha'))
    tags.reverse()
    for node, nxt in xml.pairwise(tags):
        # neighbors?
        if (nxt is node.getprevious()
                and (node.attrib['type'].strip() != '1')):
            xml.merge(nxt, node)
            node.getparent().remove(node)
