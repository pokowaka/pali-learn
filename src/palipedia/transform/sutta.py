# Sutta specific transformers.
import importlib.resources as pkg_resources
import os
import re

from lxml import etree
from unidecode import unidecode

import palipedia.data
import palipedia.transform.xml as xml
from palipedia.dirtools import InDirectory
from pathlib import Path


class TipitikaTransformer:
    """Transforms the Pali scriptures data into a usable XML tree."""

    def __init__(self, toc_file: str, dest_dir: str):
        """Initialize the transformer.

        Args:
            toc_file: The table of contents file for the scriptures.
            dest_dir: The directory where the resulting XML tree will be saved.
        """
        cleanup_xsl = pkg_resources.read_text(palipedia.data, "cleanup.xsl")
        self.xlst = etree.XSLT(etree.fromstring(cleanup_xsl))
        self.toc_file = Path(toc_file).resolve()
        self.dest_dir = Path(dest_dir).resolve()

    def transform(self):
        """Transform the Pali scriptures data into an XML tree."""
        dirname = self.toc_file.parent
        basename = self.toc_file.name
        tree = etree.Element("root", {}, {"xi": xml.XI})
        with InDirectory(dirname) as d:
            self._proc_tree(xml.parse(basename), tree, 0)

        xml.write_xml(self.dest_dir / "toc.xml", tree)

    def _proc_tree(self, tree, nxt, depth):
        tagl = ["collection", "pitika", "nikaya", "book", "chapter"]
        for node in tree:
            if len(node.attrib) == 0:
                self._proc_tree(node, nxt, depth + 1)
                continue

            subtree = etree.SubElement(
                nxt, tagl[depth], {"title": xml.xstr(node.get("text"))}
            )
            if "src" in node.attrib:
                # We are still indexing.
                next_tree = xml.parse(node.get("src"))
                self._proc_tree(next_tree, subtree, depth + 1)
            elif "action" in node.attrib:
                # This is a chapter with the actual sutta
                next_tree = xml.parse(node.get("action"))
                nodes = self._proc_chapter(next_tree)
                subtree.tag = "chapter"
                subtree.getparent().tag = "book"
                for n in nodes:
                    subtree.append(n)
                fname = str(self._path_name(subtree).with_suffix(".xml"))
                nxt.remove(subtree)
                xml.append_external(nxt, subtree, fname, self.dest_dir)
            elif "text" in node.attrib:
                # sometimes there are empty intermediate nodes..
                self._proc_tree(node, subtree, depth + 1)

        return nxt

    def _proc_chapter(self, tree):
        root = self.xlst(tree).getroot()
        # Let's make it all consistent..
        xml.remove(root, ["chapter", "book", "nikaya"])
        for child in ["chapter", "section", "subsection"]:
            xml.siblings_to_child(root, child)

        # Some cleaning steps..
        self._merge_verses(root)
        self._lift_numbers(root)
        xml.trim_text(root)
        self._extract_nr_from_title(root)
        return root

    def _path_name(self, node):
        if node is None:
            return Path()

        return Path(self._path_name(node.getparent())) / unidecode(node.get("title", ""))

    def _extract_nr_from_title(self, tree: etree.Element) -> None:
        """Extracts and sets the 'nr' attribute from the 'title' attribute of elements in a given lxml tree.

        Args:
        - tree (etree.Element): A parsed lxml tree.

        Returns:
        - None: This function doesn't return anything. It updates the lxml tree in place.

        Raises:
        - No explicit exceptions raised.

        """
        for node in tree.xpath("//*[@title]"):
            # Extract the number from the title
            m = re.match("([0-9\-]*)\. (.*)", node.get("title"))
            if m:
                # If number is successfully extracted, set 'nr' attribute and update 'title' attribute
                node.set("nr", m.group(1))
                node.set("title", m.group(2))

    def _lift_numbers(self, tree):
        """
        For each 'number' element in the XML tree, lift the 'nr' attribute up to its parent 'p' element, and remove the
        'number' element. If the next sibling element of the 'number' element is a 'verse' element, lift the 'nr'
        attribute to that 'verse' element.

        Args:
            tree (Element): The XML tree to process.
        """
        for node in tree.xpath("//number"):
            # Get the parent and next sibling elements of the 'number' element.
            parent = node.getparent()
            nxt = node.getnext()

            # If the parent is a 'p' tag, set its 'nr' attribute to the 'nr' attribute of the 'number' element, and
            # concatenate the 'tail' text of the 'number' element to the 'text' of the 'p' element.
            if parent.tag == "p":
                parent.set("nr", node.get("nr"))
                if node.tail:
                    parent.text = node.tail + xml.xstr(parent.text)

            # If the next sibling element is a 'verse' tag, set its 'nr' attribute to the 'nr' attribute of the
            # 'number' element.
            if nxt is not None and nxt.tag == "verse":
                nxt.set("nr", node.get("nr"))

            # Remove the 'number' element.
            parent.remove(node)

    def _merge_verses(self, xml_tree: etree.Element) -> None:
        """Merges adjacent <verse> elements in the given XML tree into a single <verse> element."""
        verses = list(xml_tree.xpath("//verse"))
        verses.reverse()

        for current_verse, next_verse in xml.pairwise(verses):
            # Check if current and next verse are neighbors and current verse has
            # an idx attribute that is not "first"
            if (
                next_verse is current_verse.getprevious()
                and current_verse.get("idx") != "first"
            ):
                xml.merge(next_verse, current_verse)
                current_verse.getparent().remove(current_verse)
            else:
                current_verse.attrib.clear()

        if verses:
            verses[-1].attrib.clear()
