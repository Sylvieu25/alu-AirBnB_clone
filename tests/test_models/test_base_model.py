#!/usr/bin/python3
"""Unit tests for the BaseModel class defined in models/base_model.py."""
import os
import unittest
import uuid
from datetime import datetime
from time import sleep

from models.base_model import BaseModel, TIME_FORMAT

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


class TestBaseModelInit(unittest.TestCase):
    """Tests for the creation of BaseModel instances."""

    def test_instance_type(self):
        """A new object is an instance of BaseModel."""
        self.assertIsInstance(BaseModel(), BaseModel)

    def test_id_is_str(self):
        """The id attribute is a string."""
        self.assertIsInstance(BaseModel().id, str)

    def test_id_is_valid_uuid4(self):
        """The id is a valid version 4 UUID."""
        self.assertEqual(uuid.UUID(BaseModel().id).version, 4)

    def test_unique_ids(self):
        """Two instances never share the same id."""
        self.assertNotEqual(BaseModel().id, BaseModel().id)

    def test_created_at_is_datetime(self):
        """The created_at attribute is a datetime object."""
        self.assertIsInstance(BaseModel().created_at, datetime)

    def test_updated_at_is_datetime(self):
        """The updated_at attribute is a datetime object."""
        self.assertIsInstance(BaseModel().updated_at, datetime)

    def test_timestamps_close_at_creation(self):
        """updated_at is set right after created_at at creation."""
        bm = BaseModel()
        self.assertLessEqual(bm.created_at, bm.updated_at)
        delta = bm.updated_at - bm.created_at
        self.assertLess(delta.total_seconds(), 1)

    def test_later_instance_has_later_created_at(self):
        """An instance created later has a later created_at."""
        bm1 = BaseModel()
        sleep(0.01)
        bm2 = BaseModel()
        self.assertLess(bm1.created_at, bm2.created_at)

    def test_public_attributes_in_dict(self):
        """id, created_at and updated_at are instance attributes."""
        bm = BaseModel()
        for key in ("id", "created_at", "updated_at"):
            self.assertIn(key, bm.__dict__)

    def test_custom_attribute(self):
        """Attributes can be added to an instance after creation."""
        bm = BaseModel()
        bm.name = "My First Model"
        bm.my_number = 89
        self.assertEqual(bm.name, "My First Model")
        self.assertEqual(bm.my_number, 89)


class TestBaseModelStr(unittest.TestCase):
    """Tests for the __str__ method of BaseModel."""

    def test_str_format(self):
        """__str__ returns [<class name>] (<id>) <__dict__>."""
        bm = BaseModel()
        expected = "[BaseModel] ({}) {}".format(bm.id, bm.__dict__)
        self.assertEqual(str(bm), expected)

    def test_str_with_custom_attribute(self):
        """__str__ includes attributes added after creation."""
        bm = BaseModel()
        bm.name = "My First Model"
        self.assertIn("'name': 'My First Model'", str(bm))

    def test_str_starts_with_class_name(self):
        """__str__ starts with the class name in brackets."""
        self.assertTrue(str(BaseModel()).startswith("[BaseModel] ("))


class TestBaseModelSave(unittest.TestCase):
    """Tests for the save method of BaseModel."""

    def test_save_updates_updated_at(self):
        """save() sets updated_at to a later datetime."""
        bm = BaseModel()
        first = bm.updated_at
        sleep(0.01)
        bm.save()
        self.assertGreater(bm.updated_at, first)

    def test_save_keeps_created_at(self):
        """save() does not change created_at."""
        bm = BaseModel()
        created = bm.created_at
        sleep(0.01)
        bm.save()
        self.assertEqual(bm.created_at, created)

    def test_save_twice(self):
        """Each call to save() moves updated_at forward."""
        bm = BaseModel()
        sleep(0.01)
        bm.save()
        first = bm.updated_at
        sleep(0.01)
        bm.save()
        self.assertGreater(bm.updated_at, first)

    def test_save_keeps_datetime_type(self):
        """updated_at is still a datetime after save()."""
        bm = BaseModel()
        bm.save()
        self.assertIsInstance(bm.updated_at, datetime)

    def test_save_with_argument(self):
        """save() does not accept arguments."""
        with self.assertRaises(TypeError):
            BaseModel().save(None)


class TestBaseModelToDict(unittest.TestCase):
    """Tests for the to_dict method of BaseModel."""

    def test_returns_dict(self):
        """to_dict() returns a dictionary."""
        self.assertIsInstance(BaseModel().to_dict(), dict)

    def test_class_key(self):
        """to_dict() adds a __class__ key with the class name."""
        self.assertEqual(BaseModel().to_dict()["__class__"], "BaseModel")

    def test_default_keys(self):
        """to_dict() contains exactly the default keys."""
        keys = {"id", "created_at", "updated_at", "__class__"}
        self.assertEqual(set(BaseModel().to_dict().keys()), keys)

    def test_id_value(self):
        """to_dict() keeps the id unchanged."""
        bm = BaseModel()
        self.assertEqual(bm.to_dict()["id"], bm.id)

    def test_timestamps_are_iso_strings(self):
        """created_at and updated_at are ISO format strings."""
        bm = BaseModel()
        d = bm.to_dict()
        self.assertIsInstance(d["created_at"], str)
        self.assertIsInstance(d["updated_at"], str)
        self.assertEqual(
            d["created_at"], bm.created_at.strftime(TIME_FORMAT))
        self.assertEqual(
            d["updated_at"], bm.updated_at.strftime(TIME_FORMAT))

    def test_timestamps_keep_microseconds(self):
        """The ISO strings keep microseconds even when they are zero."""
        bm = BaseModel()
        bm.created_at = datetime(2017, 9, 28, 21, 3, 54)
        self.assertEqual(
            bm.to_dict()["created_at"], "2017-09-28T21:03:54.000000")

    def test_iso_strings_convert_back(self):
        """The ISO strings convert back to the original datetimes."""
        bm = BaseModel()
        d = bm.to_dict()
        self.assertEqual(
            datetime.fromisoformat(d["created_at"]), bm.created_at)
        self.assertEqual(
            datetime.fromisoformat(d["updated_at"]), bm.updated_at)

    def test_custom_attributes_included(self):
        """to_dict() includes attributes added after creation."""
        bm = BaseModel()
        bm.name = "My First Model"
        bm.my_number = 89
        d = bm.to_dict()
        self.assertEqual(d["name"], "My First Model")
        self.assertEqual(d["my_number"], 89)

    def test_does_not_modify_instance(self):
        """to_dict() leaves the instance attributes unchanged."""
        bm = BaseModel()
        bm.to_dict()
        self.assertNotIn("__class__", bm.__dict__)
        self.assertIsInstance(bm.created_at, datetime)
        self.assertIsInstance(bm.updated_at, datetime)

    def test_differs_from_instance_dict(self):
        """to_dict() returns a new dict, not the instance __dict__."""
        bm = BaseModel()
        self.assertIsNot(bm.to_dict(), bm.__dict__)

    def test_with_argument(self):
        """to_dict() does not accept arguments."""
        with self.assertRaises(TypeError):
            BaseModel().to_dict(None)


class TestBaseModelFromDict(unittest.TestCase):
    """Tests for re-creating a BaseModel instance from a dictionary."""

    def setUp(self):
        """Create an instance and its dictionary representation."""
        self.bm = BaseModel()
        self.bm.name = "My_First_Model"
        self.bm.my_number = 89
        self.bm_dict = self.bm.to_dict()

    def test_same_attributes(self):
        """The new instance has exactly the same attributes."""
        new_bm = BaseModel(**self.bm_dict)
        self.assertEqual(new_bm.__dict__, self.bm.__dict__)

    def test_same_id(self):
        """The new instance keeps the original id."""
        self.assertEqual(BaseModel(**self.bm_dict).id, self.bm.id)

    def test_dates_are_datetime(self):
        """created_at and updated_at are converted back to datetime."""
        new_bm = BaseModel(**self.bm_dict)
        self.assertIsInstance(new_bm.created_at, datetime)
        self.assertIsInstance(new_bm.updated_at, datetime)

    def test_dates_values(self):
        """created_at and updated_at keep their original values."""
        new_bm = BaseModel(**self.bm_dict)
        self.assertEqual(new_bm.created_at, self.bm.created_at)
        self.assertEqual(new_bm.updated_at, self.bm.updated_at)

    def test_class_key_not_attribute(self):
        """The __class__ key is not added as an attribute."""
        new_bm = BaseModel(**self.bm_dict)
        self.assertNotIn("__class__", new_bm.__dict__)
        self.assertIs(type(new_bm), BaseModel)

    def test_custom_attributes(self):
        """Custom attributes are re-created with their values."""
        new_bm = BaseModel(**self.bm_dict)
        self.assertEqual(new_bm.name, "My_First_Model")
        self.assertEqual(new_bm.my_number, 89)

    def test_not_same_object(self):
        """The new instance is a different object from the original."""
        new_bm = BaseModel(**self.bm_dict)
        self.assertIsNot(new_bm, self.bm)

    def test_str_matches(self):
        """The new instance prints the same as the original."""
        self.assertEqual(str(BaseModel(**self.bm_dict)), str(self.bm))

    def test_round_trip(self):
        """to_dict() of the new instance equals the original dict."""
        new_bm = BaseModel(**self.bm_dict)
        self.assertEqual(new_bm.to_dict(), self.bm_dict)

    def test_from_known_dict(self):
        """An instance is created from a hand-written dictionary."""
        data = {
            "id": "56d43177-cc5f-4d6c-a0c1-e167f8c27337",
            "created_at": "2017-09-28T21:03:54.052298",
            "updated_at": "2017-09-28T21:03:54.052302",
            "__class__": "BaseModel",
            "name": "My_First_Model",
        }
        bm = BaseModel(**data)
        self.assertEqual(bm.id, data["id"])
        self.assertEqual(
            bm.created_at, datetime(2017, 9, 28, 21, 3, 54, 52298))
        self.assertEqual(
            bm.updated_at, datetime(2017, 9, 28, 21, 3, 54, 52302))
        self.assertEqual(bm.name, "My_First_Model")

    def test_empty_kwargs_creates_new(self):
        """Empty kwargs create a brand new instance."""
        bm = BaseModel(**{})
        self.assertIsInstance(bm.id, str)
        self.assertIsInstance(bm.created_at, datetime)
        self.assertNotEqual(bm.id, self.bm.id)

    def test_partial_kwargs_keep_defaults(self):
        """Missing id and dates in kwargs get default values."""
        bm = BaseModel(name="Partial")
        self.assertEqual(bm.name, "Partial")
        self.assertIsInstance(bm.id, str)
        self.assertIsInstance(bm.created_at, datetime)
        self.assertIsInstance(bm.updated_at, datetime)

    def test_args_are_ignored(self):
        """Positional arguments are not used."""
        bm = BaseModel("unused", 12)
        self.assertNotIn("unused", bm.__dict__.values())
        self.assertIsInstance(bm.id, str)

    def test_args_and_kwargs(self):
        """With args and kwargs, only kwargs are used."""
        bm = BaseModel("unused", **self.bm_dict)
        self.assertEqual(bm.id, self.bm.id)

    def test_invalid_date_raises(self):
        """A date string in the wrong format raises ValueError."""
        with self.assertRaises(ValueError):
            BaseModel(id="1", created_at="28/09/2017",
                      updated_at="28/09/2017")

    def test_zero_microseconds_round_trip(self):
        """A datetime with zero microseconds survives the round trip."""
        self.bm.created_at = datetime(2017, 9, 28, 21, 3, 54)
        new_bm = BaseModel(**self.bm.to_dict())
        self.assertEqual(new_bm.created_at, self.bm.created_at)


if __name__ == "__main__":
    unittest.main()
