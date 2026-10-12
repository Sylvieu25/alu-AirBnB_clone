#!/usr/bin/python3
"""Unit tests for the FileStorage class in models/engine/file_storage.py."""
import json
import os
import unittest

import models
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage

FILE = "file.json"
BACKUP = "file.json.bak"


def setUpModule():
    """Move the real file.json out of the way before the tests run."""
    if os.path.exists(FILE):
        os.rename(FILE, BACKUP)


def tearDownModule():
    """Put the real file.json back after the tests run."""
    if os.path.exists(FILE):
        os.remove(FILE)
    if os.path.exists(BACKUP):
        os.rename(BACKUP, FILE)


class TestFileStorageBase(unittest.TestCase):
    """Base class that gives every test an empty storage and no file."""

    def setUp(self):
        """Empty the stored objects and remove the JSON file."""
        FileStorage._FileStorage__objects = {}
        if os.path.exists(FILE):
            os.remove(FILE)

    def tearDown(self):
        """Empty the stored objects and remove the JSON file."""
        FileStorage._FileStorage__objects = {}
        if os.path.exists(FILE):
            os.remove(FILE)


class TestFileStorageAttributes(TestFileStorageBase):
    """Tests for the class attributes of FileStorage."""

    def test_instance_type(self):
        """FileStorage() creates a FileStorage instance."""
        self.assertIsInstance(FileStorage(), FileStorage)

    def test_file_path_value(self):
        """__file_path is the string 'file.json'."""
        self.assertEqual(FileStorage._FileStorage__file_path, FILE)

    def test_file_path_is_private(self):
        """__file_path cannot be accessed by its plain name."""
        with self.assertRaises(AttributeError):
            FileStorage.__file_path

    def test_objects_is_dict(self):
        """__objects is a dictionary."""
        self.assertIsInstance(FileStorage._FileStorage__objects, dict)

    def test_objects_is_private(self):
        """__objects cannot be accessed by its plain name."""
        with self.assertRaises(AttributeError):
            FileStorage.__objects

    def test_storage_instance(self):
        """models.storage is a FileStorage instance."""
        self.assertIsInstance(models.storage, FileStorage)

    def test_init_with_argument(self):
        """FileStorage() does not accept arguments."""
        with self.assertRaises(TypeError):
            FileStorage(None)


class TestFileStorageAll(TestFileStorageBase):
    """Tests for the all method of FileStorage."""

    def test_returns_dict(self):
        """all() returns a dictionary."""
        self.assertIsInstance(models.storage.all(), dict)

    def test_returns_objects(self):
        """all() returns the __objects dictionary itself."""
        self.assertIs(models.storage.all(),
                      FileStorage._FileStorage__objects)

    def test_empty_at_start(self):
        """all() is empty when nothing was created."""
        self.assertEqual(models.storage.all(), {})

    def test_with_argument(self):
        """all() does not accept arguments."""
        with self.assertRaises(TypeError):
            models.storage.all(None)


class TestFileStorageNew(TestFileStorageBase):
    """Tests for the new method of FileStorage."""

    def test_new_instance_is_stored(self):
        """Creating a BaseModel adds it to storage automatically."""
        bm = BaseModel()
        key = "BaseModel.{}".format(bm.id)
        self.assertIn(key, models.storage.all())
        self.assertIs(models.storage.all()[key], bm)

    def test_new_adds_object(self):
        """new() adds an object with the key <class name>.<id>."""
        bm = BaseModel(id="1234", created_at="2017-09-28T21:03:54.052298",
                       updated_at="2017-09-28T21:03:54.052298")
        self.assertNotIn("BaseModel.1234", models.storage.all())
        models.storage.new(bm)
        self.assertIs(models.storage.all()["BaseModel.1234"], bm)

    def test_from_dict_not_stored(self):
        """An instance created from a dictionary is not added."""
        bm = BaseModel()
        FileStorage._FileStorage__objects = {}
        BaseModel(**bm.to_dict())
        self.assertEqual(models.storage.all(), {})

    def test_several_objects(self):
        """Every new instance gets its own key."""
        bm1 = BaseModel()
        bm2 = BaseModel()
        self.assertEqual(len(models.storage.all()), 2)
        self.assertIn("BaseModel.{}".format(bm1.id), models.storage.all())
        self.assertIn("BaseModel.{}".format(bm2.id), models.storage.all())

    def test_new_with_none(self):
        """new(None) raises AttributeError."""
        with self.assertRaises(AttributeError):
            models.storage.new(None)

    def test_new_without_argument(self):
        """new() requires an argument."""
        with self.assertRaises(TypeError):
            models.storage.new()


class TestFileStorageSave(TestFileStorageBase):
    """Tests for the save method of FileStorage."""

    def test_save_creates_file(self):
        """save() creates the JSON file."""
        BaseModel()
        models.storage.save()
        self.assertTrue(os.path.exists(FILE))

    def test_save_content(self):
        """The file contains every object as a dictionary."""
        bm = BaseModel()
        bm.name = "My_First_Model"
        models.storage.save()
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        key = "BaseModel.{}".format(bm.id)
        self.assertEqual(data[key], bm.to_dict())

    def test_save_empty_storage(self):
        """save() with no objects writes an empty JSON object."""
        models.storage.save()
        with open(FILE, "r", encoding="utf-8") as f:
            self.assertEqual(json.load(f), {})

    def test_base_model_save_writes_file(self):
        """BaseModel.save() writes the object to the file."""
        bm = BaseModel()
        bm.save()
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("BaseModel.{}".format(bm.id), data)

    def test_save_with_argument(self):
        """save() does not accept arguments."""
        with self.assertRaises(TypeError):
            models.storage.save(None)


class TestFileStorageReload(TestFileStorageBase):
    """Tests for the reload method of FileStorage."""

    def test_reload_restores_objects(self):
        """reload() re-creates the objects saved in the file."""
        bm = BaseModel()
        bm.name = "My_First_Model"
        bm.save()
        key = "BaseModel.{}".format(bm.id)
        FileStorage._FileStorage__objects = {}
        models.storage.reload()
        self.assertIn(key, models.storage.all())
        reloaded = models.storage.all()[key]
        self.assertIsInstance(reloaded, BaseModel)
        self.assertIsNot(reloaded, bm)
        self.assertEqual(reloaded.to_dict(), bm.to_dict())

    def test_reload_without_file(self):
        """reload() does nothing when the file does not exist."""
        models.storage.reload()
        self.assertEqual(models.storage.all(), {})

    def test_reload_several_objects(self):
        """reload() restores every saved object."""
        BaseModel()
        BaseModel()
        models.storage.save()
        FileStorage._FileStorage__objects = {}
        models.storage.reload()
        self.assertEqual(len(models.storage.all()), 2)

    def test_reload_with_argument(self):
        """reload() does not accept arguments."""
        with self.assertRaises(TypeError):
            models.storage.reload(None)


if __name__ == "__main__":
    unittest.main()
