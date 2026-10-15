#!/usr/bin/python3
"""Unit tests for the State class defined in models/state.py."""
import os
import unittest
from datetime import datetime

import models
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from models.state import State

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


class TestStateAttributes(unittest.TestCase):
    """Tests for the attributes of the State class."""

    def setUp(self):
        """Define the expected class attributes and their types."""
        self.expected = {
            "name": ("", str),
        }

    def test_is_subclass(self):
        """State inherits from BaseModel."""
        self.assertTrue(issubclass(State, BaseModel))
        self.assertIsInstance(State(), BaseModel)

    def test_class_attributes_defaults(self):
        """Every class attribute has the right default value and type."""
        for name, (value, kind) in self.expected.items():
            self.assertEqual(getattr(State, name), value)
            self.assertIs(type(getattr(State, name)), kind)

    def test_attributes_are_class_attributes(self):
        """The attributes belong to the class, not to new instances."""
        obj = State()
        for name in self.expected:
            self.assertIn(name, State.__dict__)
            self.assertNotIn(name, obj.__dict__)

    def test_inherited_attributes(self):
        """A State has an id, created_at and updated_at."""
        obj = State()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_unique_ids(self):
        """Two instances never share the same id."""
        self.assertNotEqual(State().id, State().id)

    def test_set_attribute(self):
        """Setting an attribute stores it on the instance only."""
        obj = State()
        obj.name = "California"
        self.assertEqual(obj.name, "California")
        self.assertEqual(State.name, "")


class TestStateMethods(unittest.TestCase):
    """Tests for the methods inherited by State."""

    def test_str(self):
        """__str__ starts with [State] and contains the id."""
        obj = State()
        expected = "[State] ({}) {}".format(obj.id, obj.__dict__)
        self.assertEqual(str(obj), expected)

    def test_to_dict(self):
        """to_dict() uses 'State' as __class__ and keeps attributes."""
        obj = State()
        obj.name = "California"
        d = obj.to_dict()
        self.assertEqual(d["__class__"], "State")
        self.assertEqual(d["name"], "California")
        self.assertIsInstance(d["created_at"], str)

    def test_from_dict(self):
        """A State can be re-created from its dictionary."""
        obj = State()
        obj.name = "California"
        new_obj = State(**obj.to_dict())
        self.assertIsInstance(new_obj, State)
        self.assertEqual(new_obj.id, obj.id)
        self.assertEqual(new_obj.name, "California")
        self.assertEqual(new_obj.created_at, obj.created_at)
        self.assertIsNot(new_obj, obj)


class TestStateStorage(unittest.TestCase):
    """Tests for saving and reloading State instances."""

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
        """A new State is added to storage with the key State.<id>."""
        obj = State()
        self.assertIn("State.{}".format(obj.id), models.storage.all())

    def test_save_updates_updated_at(self):
        """save() moves updated_at forward."""
        obj = State()
        first = obj.updated_at
        obj.save()
        self.assertGreaterEqual(obj.updated_at, first)

    def test_save_and_reload(self):
        """A saved State is reloaded as a State with its attributes."""
        obj = State()
        obj.name = "California"
        obj.save()
        key = "State.{}".format(obj.id)
        FileStorage._FileStorage__objects = {}
        models.storage.reload()
        reloaded = models.storage.all()[key]
        self.assertIsInstance(reloaded, State)
        self.assertEqual(reloaded.name, "California")
        self.assertEqual(reloaded.to_dict(), obj.to_dict())

    def test_in_storage_classes(self):
        """FileStorage knows the State class."""
        self.assertIs(models.storage.classes()["State"], State)


if __name__ == "__main__":
    unittest.main()
