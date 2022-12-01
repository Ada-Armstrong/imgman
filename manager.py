import logging
import shutil
import imagehash

from glob import glob
from tqdm import tqdm
from PIL import Image, ImageChops
from PIL.ExifTags import TAGS
from collections import defaultdict


class ImageManager:
    """
    A class to find, copy, move, and delete images.
    """
    def __init__(self, display_loading_bar=False, logger_name="ImageManager"):
        self.display_loading_bar = display_loading_bar
        self.logger = logging.getLogger(logger_name)
        self.hashes = defaultdict(list) # img hashes to find duplicates

    def _progress(self, iterable):
        return tqdm(iterable) if self.display_loading_bar else iterable

    def find(self, directories, file_extensions=["jpg", "jpeg", "png"]):
        """
        Returns a list of file names with the given extensions in directories.
        """
        if isinstance(directories) is str:
            directories = [directories]
        self.logger.info(f"Searching for files with extensions: {file_extensions} in {directories}")

        return [f for d in directories for ext in file_extensions for f in glob(f'{d}/*.{ext}')]

    def copy(self, imgs, directory, move=False):
        """
        Copy the imgs to the directory. If imgs is a list then directory must be
        a valid dir. If imgs is a dictionary the keys are used as the destination
        directories with the directory argument prepended.
        """
        if not isinstance(imgs, list) or isinstance(imgs, dict):
            raise TypeError("imgs must be a list or a dict")

        msg = f"imgs to {directory}"
        if move:
            func = shutil.move
            msg = "Moving " + msg
        else:
            func = shutil.copy2
            msg = "Copying " + msg

        self.logger.info(msg)

        if isinstance(imgs, list):
            for img in self._progress(imgs):
                func(img, directory)
        else:
            for d in self._progress(imgs.values()):
                for img in imgs[d]:
                    func(img, f"{directory}/{d}")

        self.logger.info("Done " + msg[0].lower() + msg[1:])

    def partition(self, imgs):
        """
        Partition the images by the year and month they were taken.
        """
        self.logger.info("Partitioning imgs")
        part = defaultdict(list)

        for fname in self._progress(imgs):
            date = self.get_date_taken(fname)
            year_month = date.split()[0][:-3] if date else "None"
            part[year_month].append(fname)

        self.logger.info(f"Partitioned imgs into {part.keys()}")
        return part

    def get_exif(self, path):
        """
        Returns the EXIF tags in a human readable dict.
        """
        return {TAGS.get(tag, tag): v for tag, v in Image.open(path).getexif().items()}

    def get_date_taken(self, path):
        """
        Return the EXIF DateTime the picture was taken.
        """
        exif = self.get_exif(path)
        return exif['DateTime'] if 'DateTime' in exif else None

    def load_hashes(self, imgs):
        """
        Clears the current hashes and fills the hashes dictionary from the imgs.
        """
        self.logger.info("Loading hashes")
        self.hashes.clear()

        for fname in self._progress(imgs):
            img = Image.open(fname)
            h = imagehash.average_hash(img)
            self.hashes[h].append(fname)

        self.logger.info(f"Loaded {len(imgs)} hashes")

    def remove_duplicates(self, imgs):
        """
        Removes the duplicates.
        """
        self.logger.info("Looking for duplicate images")

        dup_count = 0
        unique_imgs = []

        for fname in self._progress(imgs):
            img = Image.open(fname)
            h = imagehash.average_hash(img)
            if h not in self.hashes:
                self.hashes[h].append(fname)
                unique_imgs.append(fname)
            else:
                unique = True
                img = img.convert("RGB")
                # cmp with each of the imgs with the same hash
                for other in self.hashes[h]:
                    oimg = Image.open(other).convert("RGB")
                    diff = ImageChops.difference(img, oimg)
                    if not diff.getbbox():
                        # images are the same
                        self.logger.debug(f"Found duplicates: {fname} and {other}")
                        dup_count += 1
                        unique = False
                        break
                if unique:
                    self.hashes[h].append(fname)
                    unique_imgs.append(fname)

        self.logger.info(f"Number of duplicates found: {dup_count}")
        return unique_imgs
