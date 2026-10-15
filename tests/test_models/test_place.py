#!/usr/bin/python3
"""Unit tests for the Place class defined in models/place.py."""
import os
import unittest
from datetime import datetime

import models
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from models.place import Place

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


class TestPlaceAttributes(unittest.TestCase):
    """Tests for the attributes of the Place class."""

    def setUp(self):
        """Define the expected class attributes and their types."""
        self.expected = {
            "city_id": ("", str),
            "user_id": ("", str),
            "name": ("", str),
            "description": ("", str),
            "number_rooms": (0, int),
            "number_bathrooms": (0, int),
            "max_guest": (0, int),
            "price_by_night": (0, int),
            "latitude": (0.0, float),
            "longitude": (0.0, float),
            "amenity_ids": ([], list),
        }

    def test_is_subclass(self):
        """Place inherits from BaseModel."""
        self.assertTrue(issubclass(Place, BaseModel))
        self.assertIsInstance(Place(), BaseModel)

    def test_class_attributes_defaults(self):
        """Every class attribute has the right default value and type."""
        for name, (value, kind) in self.expected.items():
            self.assertEqual(getattr(Place, name), value)
            self.assertIs(type(getattr(Place, name)), kind)

    def test_attributes_are_class_attributes(self):
        """The attributes belong to the class, not to new instances."""
        obj = Place()
        for name in self.expected:
            self.assertIn(name, Place.__dict__)
            self.assertNotIn(name, obj.__dict__)

    def test_inherited_attributes(self):
        """A Place has an id, created_at and updated_at."""
        obj = Place()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_unique_ids(self):
        """Two instances never share the same id."""
        self.assertNotEqual(Place().id, Place().id)

    def test_set_attribute(self):
        """Setting an attribute stores it on the instance only."""
        obj = Place()
        obj.name = "Lovely loft"
        self.assertEqual(obj.name, "Lovely loft")
        self.assertEqual(Place.name, "")


class TestPlaceMethods(unittest.TestCase):
    """Tests for the methods inherited by Place."""

    def test_str(self):
        """__str__ starts with [Place] and contains the id."""
        obj = Place()
        expected = "[Place] ({}) {}".format(obj.id, obj.__dict__)
        self.assertEqual(str(obj), expected)

    def test_to_dict(self):
        """to_dict() uses 'Place' as __class__ and keeps attributes."""
        obj = Place()
        obj.name = "Lovely loft"
        d = obj.to_dict()
        self.assertEqual(d["__class__"], "Place")
        self.assertEqual(d["name"], "Lovely loft")
        self.assertIsInstance(d["created_at"], str)

    def test_from_dict(self):
        """A Place can be re-created from its dictionary."""
        obj = Place()
        obj.name = "Lovely loft"
        new_obj = Place(**obj.to_dict())
        self.assertIsInstance(new_obj, Place)
        self.assertEqual(new_obj.id, obj.id)
        self.assertEqual(new_obj.name, "Lovely loft")
        self.assertEqual(new_obj.created_at, obj.created_at)
        self.assertIsNot(new_obj, obj)


class TestPlaceStorage(unittest.TestCase):
    """Tests for saving and reloading Place instances."""

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
        """A new Place is added to storage with the key Place.<id>."""
        obj = Place()
        self.assertIn("Place.{}".format(obj.id), models.storage.all())

    def test_save_updates_updated_at(self):
        """save() moves updated_at forward."""
        obj = Place()
        first = obj.updated_at
        obj.save()
        self.assertGreaterEqual(obj.updated_at, first)

    def test_save_and_reload(self):
        """A saved Place is reloaded as a Place with its attributes."""
        obj = Place()
        obj.name = "Lovely loft"
        obj.save()
        key = "Place.{}".format(obj.id)
        FileStorage._FileStorage__objects = {}
        models.storage.reload()
        reloaded = models.storage.all()[key]
        self.assertIsInstance(reloaded, Place)
        self.assertEqual(reloaded.name, "Lovely loft")
        self.assertEqual(reloaded.to_dict(), obj.to_dict())

    def test_in_storage_classes(self):
        """FileStorage knows the Place class."""
        self.assertIs(models.storage.classes()["Place"], Place)


if __name__ == "__main__":
    unittest.main()
