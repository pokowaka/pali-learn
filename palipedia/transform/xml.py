'''Contains functions to manipulate XML. Used to transform the source data'''
import itertools
import os

from absl import logging
from lxml import etree
from unidecode import unidecode

DEFAULT_PARSER = etree.XMLParser(remove_blank_text=True)
XI = 'http://www.w3.org/2001/XInclude'


def pairwise(iterable):
    '''s -> (s0,s1), (s1,s2), (s2, s3), ...'''
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def parse(fname, parser=DEFAULT_PARSER):
    logging.info('parsing %s', fname)
    with open(fname, 'rb') as f:
        return etree.parse(f, parser).getroot()


def xstr(s):
    if s is None:
        return ''
    return str(s)


def depth(tree):
    if tree is None:
        return 0
    return 1 + depth(tree.getparent())


def getroot(tree):
    if tree.getparent() is None:
        return tree
    return getroot(tree.getparent())


def append_external(node, child, fname, outdir):
    name = unidecode(fname)
    final_dest = os.path.join(outdir, name)
    os.makedirs(os.path.dirname(final_dest), exist_ok=True)
    etree.SubElement(node, '{' + XI + '}include', {'href': name})
    write_xml(final_dest, child)


def trim_text(tree):
    for node in tree.iter('*'):
        if node.text:
            node.text = node.text.strip()
        if node.tail:
            node.tail = node.tail.strip()


def merge(n1, n2, text_sep=''):
    '''Merge two elements with the same tag together

       Note, the attributes will not be merged.
    '''
    if n1.tag == n2.tag:
        if len(n1) > 0:
            n1[-1:][0].tail = xstr(n1[-1:][0].tail) + text_sep + xstr(n2.text)
        else:
            n1.text = xstr(n1.text) + text_sep + xstr(n2.text)
        if len(n2) > 0:
            for kid in n2.getchildren():
                n1.append(kid)


def neighbor_to_child(tree, tags):
    '''Makes all neighbors of the given tags a child of them.

    Every tag in the set of tags will be considered on the same level.
    For examle: neighbor_to_chile(<a/><b/><c/>, ['a', 'b']) ->
        <a/><b><c/></b>
    '''
    xpath = '//' + '|//'.join(tags)
    for node in tree.xpath(xpath):
        nxt = node.getnext()
        while nxt is not None and nxt.tag not in tags:
            tmp = nxt.getnext()
            nxt.getparent().remove(nxt)
            node.append(nxt)
            nxt = tmp


def path(elem):
    if elem is None:
        return ""
    return path(elem.getparent()) + "-" + elem.tag


def text_to_attr(tree, tag, attr):
    '''Lift the text and set it as an attribute.

    text_to_attr(<a>hello</a>, 'a', 'txt') => <a txt='hello'/>
    '''
    for node in tree.xpath('//' + tag):
        if len(node) > 0:
            raise "Has kids!"
        node.attrib[attr] = node.text
        node.text = None


def remove_query(tree, query):
    for node in tree.xpath(query):
        node.getparent().remove(node)


def remove(tree, tags):
    '''Removes all the given tags.'''
    query = '//' + '|//'.join(tags)
    for node in tree.xpath(query):
        node.getparent().remove(node)


def write_xml(xml_file, tree):
    logging.info("Writing %s", xml_file)
    with open(xml_file, 'wb') as res:
        root = etree.ElementTree(tree)
        root.write(res, encoding='utf-8',
                   xml_declaration=True, pretty_print=True)


def siblings_to_child(tree, tag):
    for node in tree.xpath("//" + tag):
        # Make every sibling a child
        nxt = node.getnext()
        while nxt is not None and nxt.tag != tag:
            following = nxt.getnext()
            nxt.getparent().remove(nxt)
            node.append(nxt)
            nxt = following


def remove_empty(tree, tags):
    '''Removes all the emty children.
       <a x='f'><a><b/></a></a> =>
       <a x='f'><b/></a>
    '''
    query = '//' + '|//'.join(tags)
    for node in tree.xpath(query):
        parent = node.getparent()
        if parent == None or not hasattr(parent, 'tag'):
            continue
        if (len(node.attrib) == 0 and parent.tag == node.tag):
            insert_at = parent.index(node)
            to_insert = list(node)
            to_insert.reverse()
            for child in to_insert:
                parent.insert(insert_at, child)
            parent.remove(node)


def rename(tree, tag, new_tag):
    '''Rename a tag.'''
    for node in tree.xpath('//' + tag):
        node.tag = new_tag


def lift_up(tree, tag):
    '''Lifts the contents of the tag to the parent.

    lift_up(<a><b>hel<c/>lo</b></a>, 'b') => <a>hel</c>lo</a>
    '''
    for node in tree.xpath('//' + tag):
        parent = node.getparent()
        parent.remove(node)
        if parent.text:
            parent.text += node.text
        else:
            parent.text = node.text
        for child in node.getchildren():
            parent.append(child)


def combine_siblings(tree, tag):
    '''Neighbors with the same tag are smushed together.

    combine_siblings('<b>1</b><b>2><b></a><b>3</b>', 'b') =>
    <b>12</b></a><b>3</b>
    '''
    tags = list(tree.xpath('//' + tag))
    tags.reverse()
    for node, nxt in pairwise(tags):
        # neighbors?
        if nxt is node.getprevious():
            merge(nxt, node)
            node.getparent().remove(node)
