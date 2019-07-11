'''Contains functions to manipulate XML. Used to transform the source :
from lxml import etree
import itertools
import re


def pairwise(iterable):
    '''s -> (s0,s1), (s1,s2), (s2, s3), ...'''
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def merge(n1, n2):
    '''Merge two elements with the same tag together

       Note, the attributes will not be merged.
    '''
    if n1.tag == n2.tag:
        if len(n1) > 0:
            n1[-1:][0].tail += n2.text
        else:
            n1.text += n2.text
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


def text_to_attr(tree, tag, attr):
    '''Lift the text and set it as an attribute.

    text_to_attr(<a>hello</a>, 'a', 'txt') => <a txt='hello'/>
    '''
    for node in tree.xpath('//' + tag):
        if len(node) > 0: raise "Has kids!"
        node.attrib[attr] = node.text
        node.text = None


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


# Sutta specific transformers.
def normalize_chapter(tree):
    '''<chapter> --> <chapter nr='xx' title='yy'>'''
    for node in tree.xpath('//chapter'):
        if len(node) > 0: raise "Has kids!"
        m = re.search('(.*)\.(.*)', node.text)
        if not m:
            node.attrib['title'] = node.text
            node.text = None
        else:
            node.attrib['nr'] = m.group(1).strip()
            node.attrib['title'] = m.group(2).strip()
            node.text = None

