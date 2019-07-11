from absl import app
from absl import flags
from absl import logging
from lxml import etree
from palipedia.dirtools import InDirectory
import os
import sys
import palipedia.transform.xml as xml
import palipedia.transform.sutta as sutta
from unidecode import unidecode


FLAGS = flags.FLAGS
flags.DEFINE_string(
    'src', 'data/tipitaka/romn/tipitaka_toc.xml', 'Path to source data xml.')
flags.DEFINE_string('out', 'tipitika/tipitika.xml', 'Path to output xml.')
flags.DEFINE_string('src/tipitika/romn/tipitaka_toc.xml',
                    'data', 'Path to source data xml.')
flags.DEFINE_boolean('merge', False, 'Merge all data into single xml file.')
flags.DEFINE_boolean('split', False, 'Split out books/nikaya')
flags.DEFINE_string('query', '/tree/tree/tree',
                    'Query used to split out subparts.')


def convert_book(fn):
    parser = etree.XMLParser(remove_blank_text=True)
    with open(fn, 'r') as f:
        tree = etree.parse(f, parser)
        root = tree.getroot()
        sutta.merge_verses(root)
        xml.neighbor_to_child(root, ['chapter'])
        str = etree.tostring(tree, encoding='utf-8',
                             xml_declaration=True, pretty_print=True)
        print(str.decode('utf-8'))


parser = etree.XMLParser(remove_blank_text=True, encoding='utf-8')


def open_and_replace(fname):
    '''Process a toc file and replaces the tree with actual contents.'''
    logging.info("Processing %s", fname)
    dirname = os.path.dirname(fname)
    basename = os.path.basename(fname)
    with InDirectory(dirname) as d:
        with open(basename, 'rb') as f:
            tree = etree.parse(f, parser)
            for node in tree.xpath('//*[@src or @action]'):
                for attr in ['src', 'action']:
                    if attr in node.attrib:
                        elem = open_and_replace(node.get(attr))
                        del node.attrib[attr]
                        node.insert(0, elem)

            return tree.getroot()


def write_out(tree):
    if sutta.is_toc(tree):
        title = tree.get('text', 'root')
        logging.info('processing %s - %s', tree, tree.attrib)
        toc = etree.Element('tree', {'title': title})
        dirname = unidecode(title)
        with InDirectory(dirname, True):
            for child in tree.getchildren():
                if child.tag is etree.Comment:
                    continue
                name, fn = write_out(child)
                etree.SubElement(
                    toc, 'tree', {'title': name, 'src': os.path.join(dirname, fn)})
        xml_file = unidecode(dirname + '.toc.xml')
        logging.info('Writing %s', xml_file)
        xml.write_xml(xml_file, toc)
        return (title, xml_file)
    else:
        name = tree.attrib['text']
        xml_file = unidecode(name + '.xml')

        logging.info('Writing %s', xml_file)
        xml.write_xml(xml_file, tree)
        return (name, xml_file)


def clean_and_split(fname):
    '''Cleans up the massive xml from the previous step, and splits it into books..'''
    with open(fname, 'rb') as f:
        logging.info('parsing %s', fname)
        tree = etree.parse(f, parser).getroot()
        logging.info('removing unneeded tags')
        # These are implied in the tree structure and are confusing things..
        xml.remove(tree, ['book', 'nikaya', 'chapter'])
        # Remove empty parent/child
        xml.remove_empty(tree, ['tree'])
        with InDirectory(FLAGS.out, True):
            write_out(tree)

def main(argv):
    del argv  # Unused.
    if FLAGS.merge:
        with open(FLAGS.out, 'wb') as res:
            tree = etree.ElementTree(open_and_replace(FLAGS.src))
            tree.write(res, encoding='utf-8',
                       xml_declaration=True, pretty_print=True)
    if FLAGS.split:
        clean_and_split(FLAGS.src)


if __name__ == '__main__':
    app.run(main)
