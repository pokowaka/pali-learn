from absl import app, flags

import palipedia.transform.sutta as sutta

FLAGS = flags.FLAGS
flags.DEFINE_string(
    "src", "pali/data/tipitaka/romn/tipitaka_toc.xml", "Path to source data xml."
)
flags.DEFINE_string("out", "tipitika", "Path to output directory.")


def main(argv):
    del argv  # Unused.
    sutta.TipitikaTransformer(FLAGS.src, FLAGS.out).transform()


if __name__ == "__main__":
    app.run(main)
