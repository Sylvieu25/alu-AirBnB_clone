#!/usr/bin/python3
"""Unit tests for the Amenity class defined in models/amenity.py."""
import os
import unittest
from datetime import datetime

import models
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from models.amenity import Amenity

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


class TestAmenityAttributes(unittest.TestCase):
    """Tests for the attributes of the Amenity class."""

    def setUp(self):
        """Define the expected class attributes and their types."""
        self.expected = {
            "name": ("", str),
        }

    def test_is_subclass(self):
        """Amenity inherits from BaseModel."""
        self.assertTrue(issubclass(Amenity, BaseModel))
        self.assertIsInstance(Amenity(), BaseModel)

    def test_class_attributes_defaults(self):
        """Every class attribute has the right default value and type."""
        for name, (value, kind) in self.expected.items():
            self.assertEqual(getattr(Amenity, name), value)
            self.assertIs(type(getattr(Amenity, name)), kind)

    def test_attributes_are_class_attributes(self):
        """The attributes belong to the class, not to new instances."""
        obj = Amenity()
        for name in self.expected:
            self.assertIn(name, Amenity.__dict__)
            self.assertNotIn(name, obj.__dict__)

    def test_inherited_attributes(self):
        """An Amenity has an id, created_at and updated_at."""
        obj = Amenity()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_unique_ids(self):
        """Two instances never share the same id."""
        self.assertNotEqual(Amenity().id, Amenity().id)

    def test_set_attribute(self):
        """Setting an attribute stores it on the instance only."""
        obj = Amenity()
        obj.name = "Wifi"
        self.assertEqual(obj.name, "Wifi")
        self.assertEqual(Amenity.name, "")


class TestAmenityMethods(unittest.TestCase):
    """Tests for the methods inherited by Amenity."""

    def test_str(self):
        """__str__ starts with [Amenity] and contains the id."""
        obj = Amenity()
        expected = "[Amenity] ({}) {}".format(obj.id, obj.__dict__)
        self.assertEqual(str(obj), expected)

    def test_to_dict(self):
        """to_dict() uses 'Amenity' as __class__ and keeps attributes."""
        obj = Amenity()
        obj.name = "Wifi"
        d = obj.to_dict()
        self.assertEqual(d["__class__"], "Amenity")
        self.assertEqual(d["name"], "Wifi")
        self.assertIsInstance(d["created_at"], str)

    def test_from_dict(self):
        """An Amenity can be re-created from its dictionary."""
        obj = Amenity()
        obj.name = "Wifi"
        new_obj = Amenity(**obj.to_dict())
        self.assertIsInstance(new_obj, Amenity)
        self.assertEqual(new_obj.id, obj.id)
        self.assertEqual(new_obj.name, "Wifi")
        self.assertEqual(new_obj.created_at, obj.created_at)
        self.assertIsNot(new_obj, obj)


class TestAmenityStorage(unittest.TestCase):
    """Tests for saving and reloading Amenity instances."""

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
        """A new Amenity is added to storage with the key Amenity.<id>."""
        obj = Amenity()
        self.assertIn("Amenity.{}".format(obj.id), models.storage.all())

    def test_save_updates_updated_at(self):
        """save() moves updated_at forward."""
        obj = Amenity()
        first = obj.updated_at
        obj.save()
        self.assertGreaterEqual(obj.updated_at, first)

    def test_save_and_reload(self):
        """A saved Amenity is reloaded as an Amenity with its attributes."""
        obj = Amenity()
        obj.name = "Wifi"
        obj.save()
        key = "Amenity.{}".format(obj.id)
        FileStorage._FileStorage__objects = {}
        models.storage.reload()
        reloaded = models.storage.all()[key]
        self.assertIsInstance(reloaded, Amenity)
        self.assertEqual(reloaded.name, "Wifi")
        self.assertEqual(reloaded.to_dict(), obj.to_dict())

    def test_in_storage_classes(self):
        """FileStorage knows the Amenity class."""
        self.assertIs(models.storage.classes()["Amenity"], Amenity)


if __name__ == "__main__":
    unittest.main()
