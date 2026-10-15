#!/usr/bin/python3
"""Unit tests for the City class defined in models/city.py."""
import os
import unittest
from datetime import datetime

import models
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from models.city import City

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


class TestCityAttributes(unittest.TestCase):
    """Tests for the attributes of the City class."""

    def setUp(self):
        """Define the expected class attributes and their types."""
        self.expected = {
            "state_id": ("", str),
            "name": ("", str),
        }

    def test_is_subclass(self):
        """City inherits from BaseModel."""
        self.assertTrue(issubclass(City, BaseModel))
        self.assertIsInstance(City(), BaseModel)

    def test_class_attributes_defaults(self):
        """Every class attribute has the right default value and type."""
        for name, (value, kind) in self.expected.items():
            self.assertEqual(getattr(City, name), value)
            self.assertIs(type(getattr(City, name)), kind)

    def test_attributes_are_class_attributes(self):
        """The attributes belong to the class, not to new instances."""
        obj = City()
        for name in self.expected:
            self.assertIn(name, City.__dict__)
            self.assertNotIn(name, obj.__dict__)

    def test_inherited_attributes(self):
        """A City has an id, created_at and updated_at."""
        obj = City()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_unique_ids(self):
        """Two instances never share the same id."""
        self.assertNotEqual(City().id, City().id)

    def test_set_attribute(self):
        """Setting an attribute stores it on the instance only."""
        obj = City()
        obj.name = "San Francisco"
        self.assertEqual(obj.name, "San Francisco")
        self.assertEqual(City.name, "")


class TestCityMethods(unittest.TestCase):
    """Tests for the methods inherited by City."""

    def test_str(self):
        """__str__ starts with [City] and contains the id."""
        obj = City()
        expected = "[City] ({}) {}".format(obj.id, obj.__dict__)
        self.assertEqual(str(obj), expected)

    def test_to_dict(self):
        """to_dict() uses 'City' as __class__ and keeps attributes."""
        obj = City()
        obj.name = "San Francisco"
        d = obj.to_dict()
        self.assertEqual(d["__class__"], "City")
        self.assertEqual(d["name"], "San Francisco")
        self.assertIsInstance(d["created_at"], str)

    def test_from_dict(self):
        """A City can be re-created from its dictionary."""
        obj = City()
        obj.name = "San Francisco"
        new_obj = City(**obj.to_dict())
        self.assertIsInstance(new_obj, City)
        self.assertEqual(new_obj.id, obj.id)
        self.assertEqual(new_obj.name, "San Francisco")
        self.assertEqual(new_obj.created_at, obj.created_at)
        self.assertIsNot(new_obj, obj)


class TestCityStorage(unittest.TestCase):
    """Tests for saving and reloading City instances."""

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

    def test_new_instance_is_stored(self):
        """A new City is added to storage with the key City.<id>."""
        obj = City()
        self.assertIn("City.{}".format(obj.id), models.storage.all())

    def test_save_updates_updated_at(self):
        """save() moves updated_at forward."""
        obj = City()
        first = obj.updated_at
        obj.save()
        self.assertGreaterEqual(obj.updated_at, first)

    def test_save_and_reload(self):
        """A saved City is reloaded as a City with its attributes."""
        obj = City()
        obj.name = "San Francisco"
        obj.save()
        key = "City.{}".format(obj.id)
        FileStorage._FileStorage__objects = {}
        models.storage.reload()
        reloaded = models.storage.all()[key]
        self.assertIsInstance(reloaded, City)
        self.assertEqual(reloaded.name, "San Francisco")
        self.assertEqual(reloaded.to_dict(), obj.to_dict())

    def test_in_storage_classes(self):
        """FileStorage knows the City class."""
        self.assertIs(models.storage.classes()["City"], City)


if __name__ == "__main__":
    unittest.main()
