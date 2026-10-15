#!/usr/bin/python3
"""Unit tests for the User class defined in models/user.py."""
import os
import unittest
from datetime import datetime

import models
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from models.user import User

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


class TestUserAttributes(unittest.TestCase):
    """Tests for the attributes of the User class."""

    def test_is_subclass(self):
        """User inherits from BaseModel."""
        self.assertTrue(issubclass(User, BaseModel))
        self.assertIsInstance(User(), BaseModel)

    def test_class_attributes_default(self):
        """email, password, first_name and last_name default to ''."""
        for name in ("email", "password", "first_name", "last_name"):
            self.assertEqual(getattr(User, name), "")
            self.assertIsInstance(getattr(User, name), str)

    def test_attributes_are_class_attributes(self):
        """The four attributes are class attributes, not instance ones."""
        user = User()
        for name in ("email", "password", "first_name", "last_name"):
            self.assertIn(name, User.__dict__)
            self.assertNotIn(name, user.__dict__)

    def test_inherited_attributes(self):
        """A User has an id, created_at and updated_at."""
        user = User()
        self.assertIsInstance(user.id, str)
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsInstance(user.updated_at, datetime)

    def test_unique_ids(self):
        """Two users never share the same id."""
        self.assertNotEqual(User().id, User().id)

    def test_set_attributes(self):
        """Setting the attributes stores them on the instance."""
        user = User()
        user.email = "airbnb@mail.com"
        user.password = "root"
        user.first_name = "Betty"
        user.last_name = "Bar"
        self.assertEqual(user.email, "airbnb@mail.com")
        self.assertEqual(user.password, "root")
        self.assertEqual(user.first_name, "Betty")
        self.assertEqual(user.last_name, "Bar")
        self.assertEqual(User.email, "")


class TestUserMethods(unittest.TestCase):
    """Tests for the methods inherited by User."""

    def test_str(self):
        """__str__ starts with [User] and contains the id."""
        user = User()
        expected = "[User] ({}) {}".format(user.id, user.__dict__)
        self.assertEqual(str(user), expected)

    def test_to_dict_class(self):
        """to_dict() uses 'User' as the __class__ value."""
        self.assertEqual(User().to_dict()["__class__"], "User")

    def test_to_dict_attributes(self):
        """to_dict() contains the attributes that were set."""
        user = User()
        user.first_name = "Betty"
        user.email = "airbnb@mail.com"
        d = user.to_dict()
        self.assertEqual(d["first_name"], "Betty")
        self.assertEqual(d["email"], "airbnb@mail.com")
        self.assertIsInstance(d["created_at"], str)

    def test_from_dict(self):
        """A User can be re-created from its dictionary."""
        user = User()
        user.first_name = "Betty"
        new_user = User(**user.to_dict())
        self.assertIsInstance(new_user, User)
        self.assertEqual(new_user.id, user.id)
        self.assertEqual(new_user.first_name, "Betty")
        self.assertEqual(new_user.created_at, user.created_at)
        self.assertIsNot(new_user, user)


class TestUserStorage(unittest.TestCase):
    """Tests for saving and reloading User instances."""

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

    def test_new_user_is_stored(self):
        """A new User is added to storage with the key User.<id>."""
        user = User()
        self.assertIn("User.{}".format(user.id), models.storage.all())

    def test_save_updates_updated_at(self):
        """save() moves updated_at forward."""
        user = User()
        first = user.updated_at
        user.save()
        self.assertGreaterEqual(user.updated_at, first)

    def test_save_and_reload(self):
        """A saved User is reloaded as a User with its attributes."""
        user = User()
        user.first_name = "Betty"
        user.email = "airbnb@mail.com"
        user.save()
        key = "User.{}".format(user.id)
        FileStorage._FileStorage__objects = {}
        models.storage.reload()
        reloaded = models.storage.all()[key]
        self.assertIsInstance(reloaded, User)
        self.assertEqual(reloaded.first_name, "Betty")
        self.assertEqual(reloaded.email, "airbnb@mail.com")
        self.assertEqual(reloaded.to_dict(), user.to_dict())

    def test_user_in_storage_classes(self):
        """FileStorage knows the User class."""
        self.assertIs(models.storage.classes()["User"], User)


if __name__ == "__main__":
    unittest.main()
