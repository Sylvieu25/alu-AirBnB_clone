#!/usr/bin/python3
"""Defines the BaseModel class, the parent class of all HBnB models."""
import uuid
from datetime import datetime

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class BaseModel:
    """Defines the common attributes and methods shared by all models."""

    def __init__(self, *args, **kwargs):
        """Initialize a new instance, or re-create one from a dictionary.

        Args:
            *args: unused.
            **kwargs: attributes of the instance, as returned by to_dict().
                If empty, a new instance with a new id is created.
        """
        if kwargs:
            for key, value in kwargs.items():
                if key == "__class__":
                    continue
                if key in ("created_at", "updated_at"):
                    value = datetime.strptime(value, TIME_FORMAT)
                setattr(self, key, value)
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = self.created_at

    def __str__(self):
        """Return the string representation of the instance."""
        return "[{}] ({}) {}".format(
            type(self).__name__, self.id, self.__dict__)

    def save(self):
        """Update the public instance attribute updated_at to now."""
        self.updated_at = datetime.now()

    def to_dict(self):
        """Return a dictionary with all keys/values of the instance.

        The dictionary contains a __class__ key with the class name,
        and created_at/updated_at converted to ISO format strings.
        """
        new_dict = self.__dict__.copy()
        new_dict["__class__"] = type(self).__name__
        new_dict["created_at"] = self.created_at.strftime(TIME_FORMAT)
        new_dict["updated_at"] = self.updated_at.strftime(TIME_FORMAT)
        return new_dict
