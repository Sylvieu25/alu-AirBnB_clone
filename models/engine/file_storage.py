#!/usr/bin/python3
"""Defines the FileStorage class, a JSON file storage engine for HBnB."""
import json


class FileStorage:
    """Serializes instances to a JSON file and deserializes them back.

    Attributes:
        __file_path (str): path to the JSON file.
        __objects (dict): all objects, stored by <class name>.<id>.
    """

    __file_path = "file.json"
    __objects = {}

    def all(self):
        """Return the dictionary of all stored objects."""
        return FileStorage.__objects

    def new(self, obj):
        """Add obj to the stored objects with the key <class name>.<id>."""
        key = "{}.{}".format(type(obj).__name__, obj.id)
        FileStorage.__objects[key] = obj

    def save(self):
        """Serialize all stored objects to the JSON file."""
        data = {key: obj.to_dict()
                for key, obj in FileStorage.__objects.items()}
        with open(FileStorage.__file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def classes(self):
        """Return the classes that can be stored, by class name."""
        from models.base_model import BaseModel

        return {"BaseModel": BaseModel}

    def reload(self):
        """Deserialize the JSON file into the stored objects.

        If the JSON file does not exist, nothing happens.
        """
        try:
            with open(FileStorage.__file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return
        classes = self.classes()
        for key, value in data.items():
            cls = classes[value["__class__"]]
            FileStorage.__objects[key] = cls(**value)
