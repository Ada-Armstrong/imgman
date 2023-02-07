import os
import shutil
import unittest
from imgman import ImageManager

class TestImageManager(unittest.TestCase):

    def _create_tmp_path(self, name):
        path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(path, name)

    def _create_dirs(self, path, file_structure):
        fname = list(file_structure.keys())[0]
        fpath = os.path.join(path, fname)
        if not file_structure[fname]:
            # this is a leaf
            open(fpath, "a").close()
        else:
            # this is a dir, means we can't have empty dirs
            os.mkdir(fpath)
            for other in file_structure[fname]:
                self._create_dirs(fpath, other)

    def setUp(self):
        self.imanager = ImageManager()

        self.tmp_dir_name = "tmp_test_dir"
        self.tmp_dir_path = self._create_tmp_path(self.tmp_dir_name)

        os.mkdir(self.tmp_dir_path)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir_path)

    def test_find(self):
        path = os.path.join(self.tmp_dir_path, self.test_find.__name__)

        file_structure = {"": [{"test.png": []},
                               {"test.jpg": []},
                               {"hi.txt": []},
                               {"hill.jpeg": []},
                               {"me.bmp": []},
                               {"level2": [
                                   {"hidden.png": []},
                                   {"secret.jpg": []}
                                   ]}
                               ]
                          }

        self._create_dirs(path, file_structure)
        extensions = ("png", "jpg", "bmp")

        expected = sorted([os.path.join(path, f) for f in os.listdir(path) if f.endswith(extensions)])
        res = sorted(self.imanager.find(path, file_extensions=extensions))

        self.assertEqual(res, expected)

    def test_find_recursive(self):
        path = os.path.join(self.tmp_dir_path, self.test_find_recursive.__name__)

        file_structure = {"": [{"test.png": []},
                               {"test.jpg": []},
                               {"hi.txt": []},
                               {"hill.jpeg": []},
                               {"me.bmp": []},
                               {"level2": [
                                   {"hidden.png": []},
                                   {"secret.jpg": []}
                                   ]}
                               ]
                          }

        self._create_dirs(path, file_structure)
        extensions = ("png", "jpg", "bmp")

        expected = sorted([os.path.join(dirpath, f) for (dirpath, dirnames, filenames) in os.walk(path) for f in filenames if f.endswith(extensions)])
        res = sorted(self.imanager.find(path, file_extensions=extensions, recursive=True))

        self.assertEqual(res, expected)

    def test_copy(self):
        src_path = os.path.join(self.tmp_dir_path, self.test_copy.__name__ + "_src")
        dst_path = os.path.join(self.tmp_dir_path, self.test_copy.__name__ + "_dst")

        file_names = ["test.png", "test.jpg", "hi.txt", "hill.jpeg", "me.bmp"]
        extensions = ["png", "jpg", "bmp"]

        # create tmp dirs
        os.mkdir(src_path)
        os.mkdir(dst_path)

        # create some files
        for fname in file_names:
            open(os.path.join(src_path, fname), "a").close()

        img_paths = self.imanager.find(src_path, file_extensions=extensions)
        self.imanager.copy(img_paths, dst_path)

        res = sorted(os.listdir(dst_path))
        expected = sorted([f for f in os.listdir(src_path) if f.endswith(tuple(extensions))])

        # clean up
        shutil.rmtree(src_path)
        shutil.rmtree(dst_path)

        self.assertEqual(res, expected)


if __name__ == "__main__":
    unittest.main()
