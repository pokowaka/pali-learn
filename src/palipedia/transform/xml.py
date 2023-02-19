"""Contains functions to manipulate XML. Used to transform the source data"""
import itertools
from pathlib import Path
from typing import Any, Tuple, List, Optional

from absl import logging
from lxml import etree
from unidecode import unidecode

DEFAULT_PARSER: etree.XMLParser = etree.XMLParser(remove_blank_text=True)
XI: str = "http://www.w3.org/2001/XInclude"


def pairwise(iterable: Any) -> Tuple:
    """
    Returns pairs of adjacent elements in an iterable.

    Args:
        iterable (Any): An iterable.

    Returns:
        Tuple: A tuple of pairs of adjacent elements in the iterable.
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def parse(fname: str, parser: etree.XMLParser = DEFAULT_PARSER) -> etree._Element:
    """
    Parses an XML file and returns the root element.

    Args:
        fname (str): The name of the XML file to parse.
        parser (etree.XMLParser, optional): The parser to use for parsing the XML file. Defaults to DEFAULT_PARSER.

    Returns:
        etree._Element: The root element of the parsed XML file.
    """
    logging.info("parsing %s", fname)
    with open(fname, "rb") as f:
        return etree.parse(f, parser).getroot()


def xstr(s: Optional[str]) -> str:
    """
    Converts a None value to an empty string and returns the string value of any other input.

    Args:
        s (Optional[str]): The input string.

    Returns:
        str: The string value of the input or an empty string if the input is None.
    """
    if s is None:
        return ""
    return str(s)


def depth(tree: etree._Element) -> int:
    """
    Computes the depth of a node in an XML tree.

    Args:
        tree (etree._Element): The node whose depth is to be computed.

    Returns:
        int: The depth of the node in the tree.
    """
    if tree is None:
        return 0
    return 1 + depth(tree.getparent())


def getroot(tree: etree._Element) -> etree._Element:
    """
    Returns the root node of an XML tree.

    Args:
        tree (etree._Element): A node in the XML tree.

    Returns:
        etree._Element: The root node of the XML tree.
    """
    if tree.getparent() is None:
        return tree
    return getroot(tree.getparent())


def append_external(
    node: etree._Element, child: etree._Element, fname: Path, outdir: str
) -> None:
    """
    Appends an external element to a node and writes the child to an output file.

    Args:
        node (etree._Element): The node to which the external element should be appended.
        child (etree._Element): The child element to be appended as an external element.
        fname (str): The name of the output file.
        outdir (str): The output directory where the file should be written.

    Returns:
        None
    """
    name = unidecode(fname)
    final_dest = Path(outdir) / name
    final_dest.parent.mkdir(parents=True, exist_ok=True)
    etree.SubElement(node, "{" + XI + "}include", {"href": name})
    write_xml(str(final_dest), child)


def trim_text(tree: etree._Element) -> None:
    """
    Trims the whitespace from the text and tail elements of an XML tree.

    Args:
        tree (etree._Element): The XML tree whose text and tail elements should be trimmed.

    Returns:
        None
    """
    for node in tree.iter("*"):
        if node.text:
            node.text = node.text.strip()
        if node.tail:
            node.tail = node.tail.strip()


def merge(n1: etree._Element, n2: etree._Element, text_sep: str = "") -> None:
    """
    Merges two elements with the same tag together. The attributes will not be merged.

    Args:
        n1 (etree._Element): The first element to be merged.
        n2 (etree._Element): The second element to be merged.
        text_sep (str): The separator to use between the text of the two elements.

    Returns:
        None
    """
    if n1.tag == n2.tag:
        if len(n1) > 0:
            n1[-1:][0].tail = xstr(n1[-1:][0].tail) + text_sep + xstr(n2.text)
        else:
            n1.text = xstr(n1.text) + text_sep + xstr(n2.text)
        if len(n2) > 0:
            for kid in n2.getchildren():
                n1.append(kid)


def neighbor_to_child(tree: etree._Element, tags: List[str]) -> None:
    """
    Makes all neighbors of the given tags a child of them.

    Every tag in the set of tags will be considered on the same level.
    For example: neighbor_to_child(<a/><b/><c/>, ['a', 'b']) ->
        <a/><b><c/></b>

    Args:
        tree (etree._Element): The root element of the XML tree.
        tags (List[str]): A list of tag names that should have their neighbors turned into children.

    Returns:
        None
    """
    xpath = "//" + "|//".join(tags)
    for node in tree.xpath(xpath):
        nxt = node.getnext()
        while nxt is not None and nxt.tag not in tags:
            tmp = nxt.getnext()
            nxt.getparent().remove(nxt)
            node.append(nxt)
            nxt = tmp


def path(elem: etree._Element) -> str:
    """
    Get the path of an element in the XML tree.

    Args:
        elem (etree._Element): The element to get the path of.

    Returns:
        str: The path of the element in the XML tree.
    """
    if elem is None:
        return ""
    return path(elem.getparent()) + "-" + elem.tag


def text_to_attr(tree: etree._Element, tag: str, attr: str) -> None:
    """
    Lift the text and set it as an attribute.

    text_to_attr(<a>hello</a>, 'a', 'txt') => <a txt='hello'/>

    Args:
        tree (etree._Element): The root element of the XML tree.
        tag (str): The name of the tag to set the attribute on.
        attr (str): The name of the attribute to set.

    Returns:
        None
    """
    for node in tree.xpath("//" + tag):
        if len(node) > 0:
            raise ValueError("Has kids!")
        node.attrib[attr] = node.text
        node.text = None


from typing import List
from lxml import etree


def remove_query(tree: etree._ElementTree, query: str) -> None:
    """
    Remove all elements matching the given query.

    Args:
        tree (etree._ElementTree): The XML tree to remove elements from.
        query (str): An XPath query string.

    Returns:
        None
    """
    for node in tree.xpath(query):
        node.getparent().remove(node)


def remove(tree: etree._ElementTree, tags: List[str]) -> None:
    """
    Remove all elements with the given tags.

    Args:
        tree (etree._ElementTree): The XML tree to remove elements from.
        tags (List[str]): A list of tag names.

    Returns:
        None
    """
    query = "//" + "|//".join(tags)
    for node in tree.xpath(query):
        node.getparent().remove(node)


def write_xml(xml_file: str, tree: etree._Element) -> None:
    """
    Write an XML tree to a file.

    Args:
        xml_file (str): The file path to write to.
        tree (etree._Element): The XML tree to write.

    Returns:
        None
    """
    root = etree.ElementTree(tree)
    logging.info("Writing %s", xml_file)
    with open(xml_file, "wb") as res:
        root.write(res, encoding="utf-8", xml_declaration=True, pretty_print=True)


def siblings_to_child(tree: etree._ElementTree, tag: str) -> None:
    """
    Move all siblings with the same tag as the given element under it as children.

    Args:
        tree (etree._ElementTree): The XML tree to operate on.
        tag (str): The tag name to search for siblings.

    Returns:
        None
    """
    for node in tree.xpath("//" + tag):
        # Make every sibling a child
        nxt = node.getnext()
        while nxt is not None and nxt.tag != tag:
            following = nxt.getnext()
            nxt.getparent().remove(nxt)
            node.append(nxt)
            nxt = following


def remove_empty(tree: etree._ElementTree, tags: List[str]) -> None:
    """
    Remove empty child elements with the given tags.

    Args:
        tree (etree._ElementTree): The XML tree to operate on.
        tags (List[str]): A list of tag names.

    Returns:
        None
    """
    query = "//" + "|//".join(tags)
    for node in tree.xpath(query):
        parent = node.getparent()
        if parent is None or not hasattr(parent, "tag"):
            continue
        if len(node.attrib) == 0 and parent.tag == node.tag:
            insert_at = parent.index(node)
            to_insert = list(node)
            to_insert.reverse()
            for child in to_insert:
                parent.insert(insert_at, child)
            parent.remove(node)


def rename(tree: etree._ElementTree, tag: str, new_tag: str) -> None:
    """
    Rename all elements with the given tag to the new tag.

    Args:
        tree (etree._ElementTree): The XML tree to operate on.
        tag (str): The tag name to search for.
        new_tag (str): The new tag name to replace the old tag.

    Returns:
        None
    """
    for node in tree.xpath("//" + tag):
        node.tag = new_tag


def lift_up(tree: etree._ElementTree, tag: str) -> None:
    """
    Lifts the contents of the tag to the parent.

    Args:
        tree (etree._ElementTree): The XML tree to operate on.
        tag (str): The tag to lift up.

    Returns:
        None
    """
    for node in tree.xpath("//" + tag):
        parent = node.getparent()
        parent.remove(node)
        if parent.text:
            parent.text += node.text
        else:
            parent.text = node.text
        for child in node.getchildren():
            parent.append(child)


def combine_siblings(tree: etree._ElementTree, tag: str) -> None:
    """
    Neighbors with the same tag are smushed together.

    combine_siblings('<b>1</b><b>2><b></a><b>3</b>', 'b') =>
    <b>12</b></a><b>3</b>

    Args:
        tree (etree._ElementTree): The XML tree to operate on.
        tag (str): The tag to combine siblings for.

    Returns:
        None
    """
    tags = list(tree.xpath("//" + tag))
    tags.reverse()
    for node, nxt in pairwise(tags):
        # neighbors?
        if nxt is node.getprevious():
            merge(nxt, node)
            node.getparent().remove(node)
