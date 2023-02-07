import logging
import shutil
import imagehash
import os
import pickle

from glob import glob
from tqdm import tqdm
from PIL import Image, ImageChops
from PIL.ExifTags import TAGS
from collections import defaultdict

HASH_FILE = ".hashes"


class ImageManager:
    """
    A class to find, copy, move, and delete images.
    """
    def __init__(self, display_loading_bar=False, logger_name="ImageManager"):
        self.display_loading_bar = display_loading_bar
        self.logger = logging.getLogger(logger_name)
        self.hashes = defaultdict(list) # img hashes to find duplicates
        self.fname2hash = dict()
        self.hash_func = imagehash.average_hash

    def _progress(self, iterable):
        return tqdm(iterable) if self.display_loading_bar else iterable

    def find(self, directories, file_extensions=["jpg", "jpeg", "png"], recursive=False, use_file=False):
        """
        Returns a list of file names with the given extensions in directories.
        """
        if isinstance(directories, str):
            directories = [directories]

        if use_file:
            # search for pickled hash dictionary
            for directory in directories:
                hash_path = f"{directory}/{HASH_FILE}"
                if ret := os.path.isfile(hash_path):
                    self.hashes.update(pickle.load(hash_path))
                else:
                    self.logger.info(f"Could not find hash file for {directory}")
                    found = False
            if not found:
                raise Exception("Missing hash file")
            # files are now the values of the hashes
            return [f for l in self.hashes.values() for f in l]

        if recursive:
            out = []
            for directory in directories:
                out.extend([x[0] for x in os.walk(directory)])
            directories = out

        self.logger.info(f"Searching for files with extensions: {file_extensions} in {directories}")

        return [f for d in directories for ext in file_extensions for f in glob(f"{d}/*.{ext}")]

    def copy(self, imgs, directory, move=False, save_hashes=False):
        """
        Copy the imgs to the directory. If imgs is a list then directory must be
        a valid dir. If imgs is a dictionary the keys are used as the destination
        directories with the directory argument prepended.
        """
        if not (isinstance(imgs, list) or isinstance(imgs, defaultdict)):
            raise TypeError("imgs must be a list or a dict")

        msg = f"imgs to {directory}"
        if move:
            func = shutil.move
            msg = "Moving " + msg
        else:
            func = shutil.copy2
            msg = "Copying " + msg

        self.logger.info(msg)

        new_hashes = defaultdict(list)

        if isinstance(imgs, list):
            for img in self._progress(imgs):
                func(img, directory)
                new_hashes[self.fname2hash[img]].append(new_path)
        else:
            for d in self._progress(imgs.keys()):
                dest_path = f"{directory}{d}"
                try:
                    os.mkdir(dest_path)
                except:
                    # dir already exists
                    pass
                for img in imgs[d]:
                    name = os.path.basename(img)
                    new_path = f"{dest_path}/{name}"
                    func(img, new_path)
                    new_hashes[self.fname2hash[img]].append(new_path)

        if save_hashes:
            file_name = f"{directory}/{HASH_FILE}"
            pickle.dump(new_hashes, file_name)
            self.logger.info(f"Saving hashes to {file_name}")

        self.logger.info("Done " + msg[0].lower() + msg[1:])

    def partition(self, imgs):
        """
        Partition the images by the year and month they were taken.
        """
        self.logger.info("Partitioning imgs")
        part = defaultdict(list)

        for fname in self._progress(imgs):
            try:
                date = self.get_date_taken(fname)
                year_month = date.split()[0][:-3] if date and len(date) >= 4 else "None"
            except:
                self.logger.warn(f"ERROR w/ {fname}")
            part[year_month].append(fname)

        self.logger.info(f"Partitioned imgs into {list(part.keys())}")
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
        dt = exif["DateTime"].strip() if "DateTime" in exif else None
        return dt.replace(":", "-") if dt else None

    def load_hashes(self, imgs):
        """
        Clears the current hashes and fills the hashes dictionary from the imgs.
        """
        self.logger.info("Loading hashes")
        self.hashes.clear()
        self.fname2hash.clear()

        for fname in self._progress(imgs):
            img = Image.open(fname)
            h = self.hash_func(img)
            self.hashes[h].append(fname)
            self.fname2hash[fname] = h

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
            h = self.hash_func(img)
            if h not in self.hashes:
                self.hashes[h].append(fname)
                self.fname2hash[fname] = h
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
                    self.fname2hash[fname] = h
                    unique_imgs.append(fname)

        self.logger.info(f"Number of duplicates found: {dup_count}")
        return unique_imgs
