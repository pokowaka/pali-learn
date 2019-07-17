# Sutta specific transformers.
import os
import re

from lxml import etree
from unidecode import unidecode

import palipedia.data
import palipedia.transform.xml as xml
from palipedia.dirtools import InDirectory

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


class TipitikaTransformer(object):
    '''Transforms the pitika data into a usable xml tree'''

    def __init__(self, toc, dest):
        CLEANUP_XSL = pkg_resources.read_text(palipedia.data, 'cleanup.xsl')
        self.xlst = etree.XSLT(etree.fromstring(CLEANUP_XSL))
        self.toc = toc
        self.dest = os.path.abspath(dest)

    def transform(self):
        dirname = os.path.dirname(self.toc)
        basename = os.path.basename(self.toc)
        tree = etree.Element("root", {}, {'xi': xml.XI})
        with InDirectory(dirname) as d:
            self._proc_tree(xml.parse(basename), tree, 0)

        xml.write_xml(os.path.join(self.dest, 'toc.xml'), tree)

    def _proc_tree(self, tree, nxt, depth):
        tagl = ['collection', 'pitika', 'nikaya', 'book', 'chapter']
        for node in tree:
            if len(node.attrib) == 0:
                self._proc_tree(node, nxt, depth + 1)
                continue

            subtree = etree.SubElement(
                nxt, tagl[depth], {'title': xml.xstr(node.get('text'))})
            if 'src' in node.attrib:
                # We are still indexing.
                next_tree = xml.parse(node.get('src'))
                self._proc_tree(next_tree, subtree, depth + 1)
            elif 'action' in node.attrib:
                # This is a chapter with the actual sutta
                next_tree = xml.parse(node.get('action'))
                nodes = self._proc_chapter(next_tree)
                subtree.tag = 'chapter'
                subtree.getparent().tag = 'book'
                for n in nodes:
                    subtree.append(n)
                fname = self._path_name(subtree) + '.xml'
                nxt.remove(subtree)
                xml.append_external(nxt, subtree, fname, self.dest)
            elif 'text' in node.attrib:
                # sometimes there are empty intermediate nodes..
                self._proc_tree(node, subtree, depth + 1)

        return nxt

    def _proc_chapter(self, tree):
        root = self.xlst(tree).getroot()
        # Let's make it all consistent..
        xml.remove(root, ['chapter', 'book', 'nikaya'])
        for child in ['chapter', 'section', 'subsection']:
            xml.siblings_to_child(root, child)

        # Some cleaning steps..
        self._merge_verses(root)
        self._lift_numbers(root)
        xml.trim_text(root)
        self._extract_nr_from_title(root)
        return root

    def _path_name(self, node):
        if node is None:
            return ''
        return os.path.join(self._path_name(node.getparent()), unidecode(node.get('title', '')))

    def _extract_nr_from_title(self, tree):
        for node in tree.xpath("//*[@title]"):
            m = re.match('([0-9\-]*)\. (.*)', node.get('title'))
            if m:
                node.set('nr', m.group(1))
                node.set('title', m.group(2))

    def _lift_numbers(self, tree):
        for node in tree.xpath('//number'):
            # 2 options:
            # parent is a <p> tag..
            parent = node.getparent()
            nxt = node.getnext()
            if parent.tag == 'p':
                parent.set('nr', node.get('nr'))
                if node.tail:
                    parent.text = node.tail + xml.xstr(parent.text)
            if nxt is not None and nxt.tag == 'verse':
                # We belong with the verse
                nxt.set('nr', node.get('nr'))
            parent.remove(node)

    def _merge_verses(self, tree):
        tags = list(tree.xpath('//verse'))
        tags.reverse()
        for node, nxt in xml.pairwise(tags):
            # neighbors?
            if (nxt is node.getprevious()
                    and node.get('idx') != 'first'):
                xml.merge(nxt, node)
                node.getparent().remove(node)
            else:
                node.attrib.clear()
        if tags:
            tags[-1].attrib.clear()
