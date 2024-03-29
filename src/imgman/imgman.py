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
    img_extensions = ["png", "PNG", "jpeg", "JPEG", "jpg", "JPG"]

    # logging
    logging.basicConfig()
    logging.getLogger("ImageManager").setLevel(logging.DEBUG)

    # load hashes of any existing images from the dst_dir
    try:
        exisiting_imgs = manager.find(args.dst_dir, use_file=True, recursive=True, file_extensions=img_extensions)
    except:
        # we failed to find a hash file so load them manually
        exisiting_imgs = manager.find(args.dst_dir, use_file=False, recursive=True, file_extensions=img_extensions)
        manager.load_hashes(exisiting_imgs)

    # collect new images and remove any duplicates
    imgs = manager.find(args.src_dir, recursive=True, file_extensions=img_extensions)
    imgs = manager.remove_duplicates(imgs)

    # partition by year and month and copy to dst_dir
    partition = manager.partition(imgs)
    manager.copy(partition, args.dst_dir, save_hashes=True)

if __name__ == "__main__":
    main()
