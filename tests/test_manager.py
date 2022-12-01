import os
import shutil
import unittest
from imgman import ImageManager

class TestImageManager(unittest.TestCase):

    def _create_tmp_dir(self, name):
        path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(path, name)

    def test_find(self):
        path = self._create_tmp_dir(self.test_find.__name__)

        file_names = ["test.png", "test.jpg", "hi.txt", "hill.jpeg", "me.bmp"]
        extensions = ["png", "jpg", "bmp"]
        expected = sorted([os.path.join(path, f) for f in file_names if f.endswith(tuple(extensions))])

        imanager = ImageManager()

        # create tmp dir
        os.mkdir(path)

        # create some files
        for fname in file_names:
            open(os.path.join(path, fname), "a").close()

        res = sorted(imanager.find(path, file_extensions=extensions))

        # clean up
        shutil.rmtree(path)

        self.assertEqual(res, expected)

    def test_copy(self):
        src_path = self._create_tmp_dir(self.test_copy.__name__ + "_src")
        dst_path = self._create_tmp_dir(self.test_copy.__name__ + "_dst")

        file_names = ["test.png", "test.jpg", "hi.txt", "hill.jpeg", "me.bmp"]
        extensions = ["png", "jpg", "bmp"]

        imanager = ImageManager()

        # create tmp dirs
        os.mkdir(src_path)
        os.mkdir(dst_path)

        # create some files
        for fname in file_names:
            open(os.path.join(src_path, fname), "a").close()

        img_paths = imanager.find(src_path, file_extensions=extensions)
        imanager.copy(img_paths, dst_path)

        res = sorted(os.listdir(dst_path))
        expected = sorted([f for f in os.listdir(src_path) if f.endswith(tuple(extensions))])

        # clean up
        shutil.rmtree(src_path)
        shutil.rmtree(dst_path)

        self.assertEqual(res, expected)



if __name__ == "__main__":
    unittest.main()
