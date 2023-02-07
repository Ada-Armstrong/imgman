import logging
import json


class Config:

    def __init__(self, file_types="", src_dir="", dest_dir="", recursive=False, delete=False, logger_name="ConfigManager"):
        # constants
        self.version = (0, 1)
        self.file_name = "imgman"
        self.option_keys = ["file types", "source dir", "destination dir", "recursive", "delete"]
        
        self.file_types = self.validate_file_types(file_types)
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.recursive = recursive
        self.delete = delete

        self.logger = logging.getLogger(logger_name)

    def validate_file_types(self, file_types):
        # a list of file extensions with out the '.'
        if not isinstance(file_types, list):
            self.logger.error(f"file_types expected to be list found {type(file_types)} instead")
            raise TypeError("file_types must be a list")

        for ext in file_types:
            if not isinstance(ext, str):
                self.logger.error(f"extension in file_types expected to be string found {type(ext)} instead")
                raise TypeError("extensions in file_types must be strings")

        return file_types

    def write_config(self, path):
        data = {
                "version": ".".join(self.version),
                "options": {
                    "file types": self.file_types,
                    "source dir": self.src_dir,
                    "destination dir": self.dest_dir,
                    "recursive": self.recursive,
                    "delete": self.delete
                }
        }

        json_obj = json.dumps(data, indent=4)

        with open(f"{path}/.{self.file_name}", "w") as f:
            f.write(json_obj)

    def read_config(self, path):
        with open(f"{path}/.{self.file_name}", "r") as f:
            json_obj = json.load(f)

        version = [int(x) for x in json_obj["version"].split(".")]
        major, minor = self.version

        if major < version[0] or (major == version[0] and minor < version[1]):
            # config version is greater than known version
            raise Exception()

        options = json_obj["options"]

        for key in self.option_keys:
            if key not in options:
                raise Exception()

        self.file_types = self.validate_file_types(options["file types"])
        self.src_dir = options["source dir"]
        self.dest_dir = options["destination dir"]
        self.recursive = options["recursive"]
        self.delete = options["delete"]
