#!/usr/bin/python3
"""Unit tests for the Review class defined in models/review.py."""
import os
import unittest
from datetime import datetime

import models
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from models.review import Review

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


class TestReviewAttributes(unittest.TestCase):
    """Tests for the attributes of the Review class."""

    def setUp(self):
        """Define the expected class attributes and their types."""
        self.expected = {
            "place_id": ("", str),
            "user_id": ("", str),
            "text": ("", str),
        }

    def test_is_subclass(self):
        """Review inherits from BaseModel."""
        self.assertTrue(issubclass(Review, BaseModel))
        self.assertIsInstance(Review(), BaseModel)

    def test_class_attributes_defaults(self):
        """Every class attribute has the right default value and type."""
        for name, (value, kind) in self.expected.items():
            self.assertEqual(getattr(Review, name), value)
            self.assertIs(type(getattr(Review, name)), kind)

    def test_attributes_are_class_attributes(self):
        """The attributes belong to the class, not to new instances."""
        obj = Review()
        for name in self.expected:
            self.assertIn(name, Review.__dict__)
            self.assertNotIn(name, obj.__dict__)

    def test_inherited_attributes(self):
        """A Review has an id, created_at and updated_at."""
        obj = Review()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_unique_ids(self):
        """Two instances never share the same id."""
        self.assertNotEqual(Review().id, Review().id)

    def test_set_attribute(self):
        """Setting an attribute stores it on the instance only."""
        obj = Review()
        obj.text = "Great stay"
        self.assertEqual(obj.text, "Great stay")
        self.assertEqual(Review.text, "")


class TestReviewMethods(unittest.TestCase):
    """Tests for the methods inherited by Review."""

    def test_str(self):
        """__str__ starts with [Review] and contains the id."""
        obj = Review()
        expected = "[Review] ({}) {}".format(obj.id, obj.__dict__)
        self.assertEqual(str(obj), expected)

    def test_to_dict(self):
        """to_dict() uses 'Review' as __class__ and keeps attributes."""
        obj = Review()
        obj.text = "Great stay"
        d = obj.to_dict()
        self.assertEqual(d["__class__"], "Review")
        self.assertEqual(d["text"], "Great stay")
        self.assertIsInstance(d["created_at"], str)

    def test_from_dict(self):
        """A Review can be re-created from its dictionary."""
        obj = Review()
        obj.text = "Great stay"
        new_obj = Review(**obj.to_dict())
        self.assertIsInstance(new_obj, Review)
        self.assertEqual(new_obj.id, obj.id)
        self.assertEqual(new_obj.text, "Great stay")
        self.assertEqual(new_obj.created_at, obj.created_at)
        self.assertIsNot(new_obj, obj)


class TestReviewStorage(unittest.TestCase):
    """Tests for saving and reloading Review instances."""

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
        """A new Review is added to storage with the key Review.<id>."""
        obj = Review()
        self.assertIn("Review.{}".format(obj.id), models.storage.all())

    def test_save_updates_updated_at(self):
        """save() moves updated_at forward."""
        obj = Review()
        first = obj.updated_at
        obj.save()
        self.assertGreaterEqual(obj.updated_at, first)

    def test_save_and_reload(self):
        """A saved Review is reloaded as a Review with its attributes."""
        obj = Review()
        obj.text = "Great stay"
        obj.save()
        key = "Review.{}".format(obj.id)
        FileStorage._FileStorage__objects = {}
        models.storage.reload()
        reloaded = models.storage.all()[key]
        self.assertIsInstance(reloaded, Review)
        self.assertEqual(reloaded.text, "Great stay")
        self.assertEqual(reloaded.to_dict(), obj.to_dict())

    def test_in_storage_classes(self):
        """FileStorage knows the Review class."""
        self.assertIs(models.storage.classes()["Review"], Review)


if __name__ == "__main__":
    unittest.main()
