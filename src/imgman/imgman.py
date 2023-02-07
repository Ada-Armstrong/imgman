import argparse
import logging
from manager import ImageManager

def arguments():
    """
    Parse the arguments of the program and return them.
    """
    parser = argparse.ArgumentParser(
            prog="imgman",
            description="The post-modern image manager"
            )

    parser.add_argument(
            "src_dir",
            action="store",
            help="The directory to monitor for new images"
            )

    parser.add_argument(
            "dst_dir",
            action="store",
            help="The directory to store the images"
            )

    return parser.parse_args()

def main():
    """
    Removes duplicate images and partitions them by date into the dst_dir.
    """
    args = arguments()
    manager = ImageManager(display_loading_bar=True)

    # logging
    logging.basicConfig()
    logging.getLogger("ImageManager").setLevel(logging.DEBUG)

    # load hashes of any existing images from the dst_dir
    exisiting_imgs = manager.find(args.dst_dir, recursive=True)
    manager.load_hashes(exisiting_imgs)

    # collect new images and remove any duplicates
    imgs = manager.find(args.src_dir)
    imgs = manager.remove_duplicates(imgs)

    # partition by year and month and copy to dst_dir
    partition = manager.partition(imgs)
    manager.copy(partition, args.dst_dir)

if __name__ == "__main__":
    main()
