from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string("src", 'data', "Path to source data xml.")


def convert_book(fn):
    parser = etree.XMLParser(remove_blank_text=True)
    with open(fn, 'r') as f:
        tree = etree.parse(f, parser)
        root = tree.getroot()
        text_to_attr(root, 'book', 'title')
        text_to_attr(root, 'nikaya', 'title')
        normalize_chapter(root)
        neighbor_to_child(root, ['nikaya', 'centered'])
        neighbor_to_child(root, ['book'])
        neighbor_to_child(root, ['chapter'])
        neighbor_to_child(root, ['hangnum'])
        tree.write(sys.stdout, encoding='utf-8', xml_declaration=True, pretty_print=True)


def main(argv):
  del argv  # Unused.
  convert_book(FLAGS.src)


if __name__ == '__main__':
  app.run(main)
