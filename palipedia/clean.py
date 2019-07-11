from absl import app
from absl import flags
from absl import logging
from lxml import etree
from palipedia.dirtools import InDirectory
import os
import sys
import palipedia.transform.xml as xml
import palipedia.transform.sutta as sutta


FLAGS = flags.FLAGS
flags.DEFINE_string(
    'src', 'data/tipitaka/romn/tipitaka_toc.xml', 'Path to source data xml.')
flags.DEFINE_string('out', 'tipitika/tipitika.xml', 'Path to output xml.')
flags.DEFINE_string('src/tipitika/romn/tipitaka_toc.xml',
                    'data', 'Path to source data xml.')
flags.DEFINE_boolean('merge', False, 'Merge all data into single xml file.')
flags.DEFINE_boolean('split', False, 'Split out books/nikaya')


def convert_book(fn):
    parser = etree.XMLParser(remove_blank_text=True)
    with open(fn, 'r') as f:
        tree = etree.parse(f, parser)
        root = tree.getroot()
        xml.text_to_attr(root, 'book', 'title')
        xml.text_to_attr(root, 'nikaya', 'title')
        sutta.normalize_chapter(root)
        sutta.merge_verses(root)
        xml.neighbor_to_child(root, ['nikaya'])
        xml.neighbor_to_child(root, ['book'])
        xml.neighbor_to_child(root, ['chapter'])
        str = etree.tostring(tree, encoding='utf-8',
                             xml_declaration=True, pretty_print=True)
        print(str.decode('utf-8'))

parser = etree.XMLParser(remove_blank_text=True)

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


def clean_and_split(fname):
    '''Cleans up the massive xml from the previous step, and splits it into books..'''
    with open(fname, 'rb') as f:
        tree = etree.parse(f, parser)
        xml.remove(tree, ['book', 'nikaya'])
        tree.getroot()





def main(argv):
  del argv  # Unused.
  if FLAGS.merge:
      with open(FLAGS.out, 'wb') as res:
        tree = etree.ElementTree(open_and_replace(FLAGS.src))
        tree.write(res, encoding='utf-8',
                  xml_declaration=True, pretty_print=True)


if __name__ == '__main__':
  app.run(main)
