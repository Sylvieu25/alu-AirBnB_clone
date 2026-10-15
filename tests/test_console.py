#!/usr/bin/python3
"""Unit tests for the HBNBCommand console defined in console.py."""
import os
import unittest
from io import StringIO
from unittest.mock import patch

import models
from console import HBNBCommand
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


class ConsoleTestCase(unittest.TestCase):
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

    def new_id(self, cls_name):
        """Create an instance with the console and return its id."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("create " + cls_name)
        return f.getvalue().strip()

    def get(self, cls_name, obj_id):
        """Return the stored instance of cls_name with obj_id, or None."""
        return models.storage.all().get("{}.{}".format(cls_name, obj_id))


class TestConsoleBasics(ConsoleTestCase):
    """Tests for the prompt, quit, EOF, empty lines and help."""

    def test_prompt(self):
        """The prompt is '(hbnb) '."""
        self.assertEqual(HBNBCommand.prompt, "(hbnb) ")

    def test_quit(self):
        """quit stops the command loop and prints nothing."""
        with patch('sys.stdout', new=StringIO()) as f:
            result = HBNBCommand().onecmd("quit")
        self.assertTrue(result)
        self.assertEqual(f.getvalue(), "")

    def test_EOF(self):
        """EOF stops the command loop and prints a new line."""
        with patch('sys.stdout', new=StringIO()) as f:
            result = HBNBCommand().onecmd("EOF")
        self.assertTrue(result)
        self.assertEqual(f.getvalue(), "\n")

    def test_empty_line(self):
        """An empty line prints nothing and does not repeat a command."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("")
        self.assertEqual(f.getvalue(), "")
        with patch('sys.stdout', new=StringIO()) as f:
            console = HBNBCommand()
            console.onecmd("help quit")
            first = f.getvalue()
            console.onecmd("")
            console.emptyline()
        self.assertIn("Quit command", first)
        self.assertEqual(f.getvalue(), first)

    def test_help(self):
        """help lists every documented command."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("help")
        for command in ("EOF", "all", "create", "destroy", "help",
                        "quit", "show", "update"):
            self.assertIn(command, f.getvalue())

    def test_help_commands(self):
        """Every command has its own help message."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("help quit")
        self.assertEqual(f.getvalue().strip(),
                         "Quit command to exit the program")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("help EOF")
        self.assertEqual(f.getvalue().strip(),
                         "EOF command to exit the program")
        for command in ("create", "show", "destroy", "all", "update"):
            with patch('sys.stdout', new=StringIO()) as f:
                HBNBCommand().onecmd("help " + command)
            self.assertNotEqual(f.getvalue().strip(), "")
            self.assertNotIn("No help", f.getvalue())

    def test_unknown_syntax(self):
        """Unknown commands print an Unknown syntax message."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("hello")
        self.assertEqual(f.getvalue().strip(), "*** Unknown syntax: hello")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("User.fly()")
        self.assertEqual(f.getvalue().strip(),
                         "*** Unknown syntax: User.fly()")


class TestConsoleErrors(ConsoleTestCase):
    """Tests for the error messages of every command."""

    def check(self, command, message):
        """Assert that command prints exactly message."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd(command)
        self.assertEqual(f.getvalue().strip(), message)

    def test_class_name_missing(self):
        """Commands without a class print class name missing."""
        for command in ("create", "show", "destroy", "update",
                        ".show()", ".destroy()", ".update()", ".count()"):
            self.check(command, "** class name missing **")

    def test_class_doesnt_exist(self):
        """Commands with an unknown class print class doesn't exist."""
        for command in ("create MyModel", "show MyModel", "destroy MyModel",
                        "all MyModel", "update MyModel", "MyModel.all()",
                        "MyModel.count()", "MyModel.show()",
                        "MyModel.destroy()", "MyModel.update()"):
            self.check(command, "** class doesn't exist **")

    def test_instance_id_missing(self):
        """Commands without an id print instance id missing."""
        for command in ("show BaseModel", "destroy BaseModel",
                        "update BaseModel", "BaseModel.show()",
                        "BaseModel.destroy()", "BaseModel.update()"):
            self.check(command, "** instance id missing **")

    def test_no_instance_found(self):
        """Commands with an unknown id print no instance found."""
        for command in ("show BaseModel 1234", "destroy BaseModel 1234",
                        "update BaseModel 1234", 'BaseModel.show("1234")',
                        'BaseModel.destroy("1234")',
                        'BaseModel.update("1234")',
                        'BaseModel.update("1234", {"a": 1})'):
            self.check(command, "** no instance found **")

    def test_attribute_name_missing(self):
        """update without an attribute prints attribute name missing."""
        obj_id = self.new_id("BaseModel")
        self.check("update BaseModel " + obj_id,
                   "** attribute name missing **")
        self.check('BaseModel.update("' + obj_id + '")',
                   "** attribute name missing **")

    def test_value_missing(self):
        """update without a value prints value missing."""
        obj_id = self.new_id("BaseModel")
        self.check("update BaseModel " + obj_id + " first_name",
                   "** value missing **")
        self.check('BaseModel.update("' + obj_id + '", "first_name")',
                   "** value missing **")


class TestConsoleCreate(ConsoleTestCase):
    """Tests for the create command."""

    def test_create_basemodel(self):
        """create BaseModel prints a new id and stores the instance."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("create BaseModel")
        obj_id = f.getvalue().strip()
        self.assertEqual(len(obj_id), 36)
        self.assertIsNotNone(self.get("BaseModel", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn("BaseModel." + obj_id, json_file.read())

    def test_create_user(self):
        """create User prints a new id and stores the instance."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("create User")
        obj_id = f.getvalue().strip()
        self.assertEqual(len(obj_id), 36)
        self.assertIsNotNone(self.get("User", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn("User." + obj_id, json_file.read())

    def test_create_state(self):
        """create State prints a new id and stores the instance."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("create State")
        obj_id = f.getvalue().strip()
        self.assertEqual(len(obj_id), 36)
        self.assertIsNotNone(self.get("State", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn("State." + obj_id, json_file.read())

    def test_create_city(self):
        """create City prints a new id and stores the instance."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("create City")
        obj_id = f.getvalue().strip()
        self.assertEqual(len(obj_id), 36)
        self.assertIsNotNone(self.get("City", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn("City." + obj_id, json_file.read())

    def test_create_amenity(self):
        """create Amenity prints a new id and stores the instance."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("create Amenity")
        obj_id = f.getvalue().strip()
        self.assertEqual(len(obj_id), 36)
        self.assertIsNotNone(self.get("Amenity", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn("Amenity." + obj_id, json_file.read())

    def test_create_place(self):
        """create Place prints a new id and stores the instance."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("create Place")
        obj_id = f.getvalue().strip()
        self.assertEqual(len(obj_id), 36)
        self.assertIsNotNone(self.get("Place", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn("Place." + obj_id, json_file.read())

    def test_create_review(self):
        """create Review prints a new id and stores the instance."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("create Review")
        obj_id = f.getvalue().strip()
        self.assertEqual(len(obj_id), 36)
        self.assertIsNotNone(self.get("Review", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn("Review." + obj_id, json_file.read())


class TestConsoleShow(ConsoleTestCase):
    """Tests for show and <class>.show()."""

    def test_show_basemodel(self):
        """show BaseModel and BaseModel.show() print the instance."""
        obj_id = self.new_id("BaseModel")
        expected = str(self.get("BaseModel", obj_id))
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("show BaseModel " + obj_id)
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('BaseModel.show("' + obj_id + '")')
        self.assertEqual(f.getvalue().strip(), expected)

    def test_show_user(self):
        """show User and User.show() print the instance."""
        obj_id = self.new_id("User")
        expected = str(self.get("User", obj_id))
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("show User " + obj_id)
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('User.show("' + obj_id + '")')
        self.assertEqual(f.getvalue().strip(), expected)

    def test_show_state(self):
        """show State and State.show() print the instance."""
        obj_id = self.new_id("State")
        expected = str(self.get("State", obj_id))
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("show State " + obj_id)
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('State.show("' + obj_id + '")')
        self.assertEqual(f.getvalue().strip(), expected)

    def test_show_city(self):
        """show City and City.show() print the instance."""
        obj_id = self.new_id("City")
        expected = str(self.get("City", obj_id))
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("show City " + obj_id)
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('City.show("' + obj_id + '")')
        self.assertEqual(f.getvalue().strip(), expected)

    def test_show_amenity(self):
        """show Amenity and Amenity.show() print the instance."""
        obj_id = self.new_id("Amenity")
        expected = str(self.get("Amenity", obj_id))
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("show Amenity " + obj_id)
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Amenity.show("' + obj_id + '")')
        self.assertEqual(f.getvalue().strip(), expected)

    def test_show_place(self):
        """show Place and Place.show() print the instance."""
        obj_id = self.new_id("Place")
        expected = str(self.get("Place", obj_id))
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("show Place " + obj_id)
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Place.show("' + obj_id + '")')
        self.assertEqual(f.getvalue().strip(), expected)

    def test_show_review(self):
        """show Review and Review.show() print the instance."""
        obj_id = self.new_id("Review")
        expected = str(self.get("Review", obj_id))
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("show Review " + obj_id)
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Review.show("' + obj_id + '")')
        self.assertEqual(f.getvalue().strip(), expected)


class TestConsoleDestroy(ConsoleTestCase):
    """Tests for destroy and <class>.destroy()."""

    def test_destroy_basemodel(self):
        """destroy BaseModel and BaseModel.destroy() delete the instance."""
        obj_id = self.new_id("BaseModel")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("destroy BaseModel " + obj_id)
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("BaseModel", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertNotIn(obj_id, json_file.read())
        obj_id = self.new_id("BaseModel")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('BaseModel.destroy("' + obj_id + '")')
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("BaseModel", obj_id))

    def test_destroy_user(self):
        """destroy User and User.destroy() delete the instance."""
        obj_id = self.new_id("User")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("destroy User " + obj_id)
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("User", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertNotIn(obj_id, json_file.read())
        obj_id = self.new_id("User")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('User.destroy("' + obj_id + '")')
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("User", obj_id))

    def test_destroy_state(self):
        """destroy State and State.destroy() delete the instance."""
        obj_id = self.new_id("State")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("destroy State " + obj_id)
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("State", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertNotIn(obj_id, json_file.read())
        obj_id = self.new_id("State")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('State.destroy("' + obj_id + '")')
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("State", obj_id))

    def test_destroy_city(self):
        """destroy City and City.destroy() delete the instance."""
        obj_id = self.new_id("City")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("destroy City " + obj_id)
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("City", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertNotIn(obj_id, json_file.read())
        obj_id = self.new_id("City")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('City.destroy("' + obj_id + '")')
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("City", obj_id))

    def test_destroy_amenity(self):
        """destroy Amenity and Amenity.destroy() delete the instance."""
        obj_id = self.new_id("Amenity")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("destroy Amenity " + obj_id)
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("Amenity", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertNotIn(obj_id, json_file.read())
        obj_id = self.new_id("Amenity")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Amenity.destroy("' + obj_id + '")')
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("Amenity", obj_id))

    def test_destroy_place(self):
        """destroy Place and Place.destroy() delete the instance."""
        obj_id = self.new_id("Place")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("destroy Place " + obj_id)
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("Place", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertNotIn(obj_id, json_file.read())
        obj_id = self.new_id("Place")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Place.destroy("' + obj_id + '")')
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("Place", obj_id))

    def test_destroy_review(self):
        """destroy Review and Review.destroy() delete the instance."""
        obj_id = self.new_id("Review")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("destroy Review " + obj_id)
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("Review", obj_id))
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertNotIn(obj_id, json_file.read())
        obj_id = self.new_id("Review")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Review.destroy("' + obj_id + '")')
        self.assertEqual(f.getvalue(), "")
        self.assertIsNone(self.get("Review", obj_id))


class TestConsoleAll(ConsoleTestCase):
    """Tests for all and <class>.all()."""

    def test_all_empty(self):
        """all with no objects prints an empty list."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("all")
        self.assertEqual(f.getvalue().strip(), "[]")

    def test_all_every_object(self):
        """all prints the objects of every class."""
        for cls_name in ("BaseModel", "User", "State", "City",
                         "Amenity", "Place", "Review"):
            self.new_id(cls_name)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("all")
        for cls_name in ("BaseModel", "User", "State", "City",
                         "Amenity", "Place", "Review"):
            self.assertIn("[{}]".format(cls_name), f.getvalue())

    def test_all_basemodel(self):
        """all BaseModel and BaseModel.all() print only BaseModel instances."""
        obj_id = self.new_id("BaseModel")
        self.new_id("User")
        expected = str([str(self.get("BaseModel", obj_id))])
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("all BaseModel")
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("BaseModel.all()")
        self.assertEqual(f.getvalue().strip(), expected)
        self.assertNotIn("[User]", f.getvalue())

    def test_all_user(self):
        """all User and User.all() print only User instances."""
        obj_id = self.new_id("User")
        self.new_id("Place")
        expected = str([str(self.get("User", obj_id))])
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("all User")
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("User.all()")
        self.assertEqual(f.getvalue().strip(), expected)
        self.assertNotIn("[Place]", f.getvalue())

    def test_all_state(self):
        """all State and State.all() print only State instances."""
        obj_id = self.new_id("State")
        self.new_id("User")
        expected = str([str(self.get("State", obj_id))])
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("all State")
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("State.all()")
        self.assertEqual(f.getvalue().strip(), expected)
        self.assertNotIn("[User]", f.getvalue())

    def test_all_city(self):
        """all City and City.all() print only City instances."""
        obj_id = self.new_id("City")
        self.new_id("User")
        expected = str([str(self.get("City", obj_id))])
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("all City")
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("City.all()")
        self.assertEqual(f.getvalue().strip(), expected)
        self.assertNotIn("[User]", f.getvalue())

    def test_all_amenity(self):
        """all Amenity and Amenity.all() print only Amenity instances."""
        obj_id = self.new_id("Amenity")
        self.new_id("User")
        expected = str([str(self.get("Amenity", obj_id))])
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("all Amenity")
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("Amenity.all()")
        self.assertEqual(f.getvalue().strip(), expected)
        self.assertNotIn("[User]", f.getvalue())

    def test_all_place(self):
        """all Place and Place.all() print only Place instances."""
        obj_id = self.new_id("Place")
        self.new_id("User")
        expected = str([str(self.get("Place", obj_id))])
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("all Place")
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("Place.all()")
        self.assertEqual(f.getvalue().strip(), expected)
        self.assertNotIn("[User]", f.getvalue())

    def test_all_review(self):
        """all Review and Review.all() print only Review instances."""
        obj_id = self.new_id("Review")
        self.new_id("User")
        expected = str([str(self.get("Review", obj_id))])
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("all Review")
        self.assertEqual(f.getvalue().strip(), expected)
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("Review.all()")
        self.assertEqual(f.getvalue().strip(), expected)
        self.assertNotIn("[User]", f.getvalue())


class TestConsoleCount(ConsoleTestCase):
    """Tests for <class>.count()."""

    def test_count_basemodel(self):
        """BaseModel.count() prints the number of BaseModel instances."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("BaseModel.count()")
        self.assertEqual(f.getvalue().strip(), "0")
        self.new_id("BaseModel")
        self.new_id("BaseModel")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("BaseModel.count()")
        self.assertEqual(f.getvalue().strip(), "2")

    def test_count_user(self):
        """User.count() prints the number of User instances."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("User.count()")
        self.assertEqual(f.getvalue().strip(), "0")
        self.new_id("User")
        self.new_id("User")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("User.count()")
        self.assertEqual(f.getvalue().strip(), "2")

    def test_count_state(self):
        """State.count() prints the number of State instances."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("State.count()")
        self.assertEqual(f.getvalue().strip(), "0")
        self.new_id("State")
        self.new_id("State")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("State.count()")
        self.assertEqual(f.getvalue().strip(), "2")

    def test_count_city(self):
        """City.count() prints the number of City instances."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("City.count()")
        self.assertEqual(f.getvalue().strip(), "0")
        self.new_id("City")
        self.new_id("City")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("City.count()")
        self.assertEqual(f.getvalue().strip(), "2")

    def test_count_amenity(self):
        """Amenity.count() prints the number of Amenity instances."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("Amenity.count()")
        self.assertEqual(f.getvalue().strip(), "0")
        self.new_id("Amenity")
        self.new_id("Amenity")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("Amenity.count()")
        self.assertEqual(f.getvalue().strip(), "2")

    def test_count_place(self):
        """Place.count() prints the number of Place instances."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("Place.count()")
        self.assertEqual(f.getvalue().strip(), "0")
        self.new_id("Place")
        self.new_id("Place")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("Place.count()")
        self.assertEqual(f.getvalue().strip(), "2")

    def test_count_review(self):
        """Review.count() prints the number of Review instances."""
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("Review.count()")
        self.assertEqual(f.getvalue().strip(), "0")
        self.new_id("Review")
        self.new_id("Review")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("Review.count()")
        self.assertEqual(f.getvalue().strip(), "2")


class TestConsoleUpdate(ConsoleTestCase):
    """Tests for update and <class>.update()."""

    def test_update_basemodel(self):
        """update BaseModel sets the attribute and saves it."""
        obj_id = self.new_id("BaseModel")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("update BaseModel " + obj_id +
                                 ' attribute_name "string value"')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("BaseModel", obj_id).attribute_name,
                         "string value")
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn('"attribute_name": "string value"',
                          json_file.read())

    def test_dot_update_basemodel(self):
        """BaseModel.update(<id>, <name>, <value>) sets the attribute."""
        obj_id = self.new_id("BaseModel")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('BaseModel.update("' + obj_id +
                                 '", "attribute_name", "string_value")')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("BaseModel", obj_id).attribute_name,
                         "string_value")

    def test_dot_update_dict_basemodel(self):
        """BaseModel.update(<id>, <dictionary>) sets every attribute."""
        obj_id = self.new_id("BaseModel")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('BaseModel.update("' + obj_id +
                                 '", {"attribute_name": "string_value", '
                                 '"age": 89})')
        self.assertEqual(f.getvalue(), "")
        obj = self.get("BaseModel", obj_id)
        self.assertEqual(obj.attribute_name, "string_value")
        self.assertEqual(obj.age, 89)

    def test_update_user(self):
        """update User sets the attribute and saves it."""
        obj_id = self.new_id("User")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("update User " + obj_id +
                                 ' attribute_name "string value"')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("User", obj_id).attribute_name,
                         "string value")
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn('"attribute_name": "string value"',
                          json_file.read())

    def test_dot_update_user(self):
        """User.update(<id>, <name>, <value>) sets the attribute."""
        obj_id = self.new_id("User")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('User.update("' + obj_id +
                                 '", "attribute_name", "string_value")')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("User", obj_id).attribute_name,
                         "string_value")

    def test_dot_update_dict_user(self):
        """User.update(<id>, <dictionary>) sets every attribute."""
        obj_id = self.new_id("User")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('User.update("' + obj_id +
                                 '", {"attribute_name": "string_value", '
                                 '"age": 89})')
        self.assertEqual(f.getvalue(), "")
        obj = self.get("User", obj_id)
        self.assertEqual(obj.attribute_name, "string_value")
        self.assertEqual(obj.age, 89)

    def test_update_state(self):
        """update State sets the attribute and saves it."""
        obj_id = self.new_id("State")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("update State " + obj_id +
                                 ' attribute_name "string value"')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("State", obj_id).attribute_name,
                         "string value")
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn('"attribute_name": "string value"',
                          json_file.read())

    def test_dot_update_state(self):
        """State.update(<id>, <name>, <value>) sets the attribute."""
        obj_id = self.new_id("State")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('State.update("' + obj_id +
                                 '", "attribute_name", "string_value")')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("State", obj_id).attribute_name,
                         "string_value")

    def test_dot_update_dict_state(self):
        """State.update(<id>, <dictionary>) sets every attribute."""
        obj_id = self.new_id("State")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('State.update("' + obj_id +
                                 '", {"attribute_name": "string_value", '
                                 '"age": 89})')
        self.assertEqual(f.getvalue(), "")
        obj = self.get("State", obj_id)
        self.assertEqual(obj.attribute_name, "string_value")
        self.assertEqual(obj.age, 89)

    def test_update_city(self):
        """update City sets the attribute and saves it."""
        obj_id = self.new_id("City")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("update City " + obj_id +
                                 ' attribute_name "string value"')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("City", obj_id).attribute_name,
                         "string value")
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn('"attribute_name": "string value"',
                          json_file.read())

    def test_dot_update_city(self):
        """City.update(<id>, <name>, <value>) sets the attribute."""
        obj_id = self.new_id("City")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('City.update("' + obj_id +
                                 '", "attribute_name", "string_value")')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("City", obj_id).attribute_name,
                         "string_value")

    def test_dot_update_dict_city(self):
        """City.update(<id>, <dictionary>) sets every attribute."""
        obj_id = self.new_id("City")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('City.update("' + obj_id +
                                 '", {"attribute_name": "string_value", '
                                 '"age": 89})')
        self.assertEqual(f.getvalue(), "")
        obj = self.get("City", obj_id)
        self.assertEqual(obj.attribute_name, "string_value")
        self.assertEqual(obj.age, 89)

    def test_update_amenity(self):
        """update Amenity sets the attribute and saves it."""
        obj_id = self.new_id("Amenity")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("update Amenity " + obj_id +
                                 ' attribute_name "string value"')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("Amenity", obj_id).attribute_name,
                         "string value")
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn('"attribute_name": "string value"',
                          json_file.read())

    def test_dot_update_amenity(self):
        """Amenity.update(<id>, <name>, <value>) sets the attribute."""
        obj_id = self.new_id("Amenity")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Amenity.update("' + obj_id +
                                 '", "attribute_name", "string_value")')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("Amenity", obj_id).attribute_name,
                         "string_value")

    def test_dot_update_dict_amenity(self):
        """Amenity.update(<id>, <dictionary>) sets every attribute."""
        obj_id = self.new_id("Amenity")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Amenity.update("' + obj_id +
                                 '", {"attribute_name": "string_value", '
                                 '"age": 89})')
        self.assertEqual(f.getvalue(), "")
        obj = self.get("Amenity", obj_id)
        self.assertEqual(obj.attribute_name, "string_value")
        self.assertEqual(obj.age, 89)

    def test_update_place(self):
        """update Place sets the attribute and saves it."""
        obj_id = self.new_id("Place")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("update Place " + obj_id +
                                 ' attribute_name "string value"')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("Place", obj_id).attribute_name,
                         "string value")
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn('"attribute_name": "string value"',
                          json_file.read())

    def test_dot_update_place(self):
        """Place.update(<id>, <name>, <value>) sets the attribute."""
        obj_id = self.new_id("Place")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Place.update("' + obj_id +
                                 '", "attribute_name", "string_value")')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("Place", obj_id).attribute_name,
                         "string_value")

    def test_dot_update_dict_place(self):
        """Place.update(<id>, <dictionary>) sets every attribute."""
        obj_id = self.new_id("Place")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Place.update("' + obj_id +
                                 '", {"attribute_name": "string_value", '
                                 '"age": 89})')
        self.assertEqual(f.getvalue(), "")
        obj = self.get("Place", obj_id)
        self.assertEqual(obj.attribute_name, "string_value")
        self.assertEqual(obj.age, 89)

    def test_update_review(self):
        """update Review sets the attribute and saves it."""
        obj_id = self.new_id("Review")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd("update Review " + obj_id +
                                 ' attribute_name "string value"')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("Review", obj_id).attribute_name,
                         "string value")
        with open(FILE, "r", encoding="utf-8") as json_file:
            self.assertIn('"attribute_name": "string value"',
                          json_file.read())

    def test_dot_update_review(self):
        """Review.update(<id>, <name>, <value>) sets the attribute."""
        obj_id = self.new_id("Review")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Review.update("' + obj_id +
                                 '", "attribute_name", "string_value")')
        self.assertEqual(f.getvalue(), "")
        self.assertEqual(self.get("Review", obj_id).attribute_name,
                         "string_value")

    def test_dot_update_dict_review(self):
        """Review.update(<id>, <dictionary>) sets every attribute."""
        obj_id = self.new_id("Review")
        with patch('sys.stdout', new=StringIO()) as f:
            HBNBCommand().onecmd('Review.update("' + obj_id +
                                 '", {"attribute_name": "string_value", '
                                 '"age": 89})')
        self.assertEqual(f.getvalue(), "")
        obj = self.get("Review", obj_id)
        self.assertEqual(obj.attribute_name, "string_value")
        self.assertEqual(obj.age, 89)

    def test_update_casts_types(self):
        """Values are cast to the type of the class attribute."""
        obj_id = self.new_id("Place")
        with patch('sys.stdout', new=StringIO()):
            HBNBCommand().onecmd("update Place " + obj_id + " max_guest 6")
            HBNBCommand().onecmd("update Place " + obj_id +
                                 " latitude 37.77")
            HBNBCommand().onecmd("update Place " + obj_id + " name 123")
        obj = self.get("Place", obj_id)
        self.assertIs(type(obj.max_guest), int)
        self.assertEqual(obj.max_guest, 6)
        self.assertIs(type(obj.latitude), float)
        self.assertEqual(obj.name, "123")

    def test_update_ignores_extra_arguments(self):
        """Only the first attribute is updated."""
        obj_id = self.new_id("User")
        with patch('sys.stdout', new=StringIO()):
            HBNBCommand().onecmd("update User " + obj_id +
                                 ' email "a@b.c" first_name "Betty"')
        obj = self.get("User", obj_id)
        self.assertEqual(obj.email, "a@b.c")
        self.assertNotIn("first_name", obj.__dict__)

    def test_update_does_not_change_id(self):
        """id cannot be changed by update."""
        obj_id = self.new_id("User")
        with patch('sys.stdout', new=StringIO()):
            HBNBCommand().onecmd("update User " + obj_id + " id 1234")
            HBNBCommand().onecmd('User.update("' + obj_id +
                                 '", {"id": "1234"})')
        self.assertEqual(self.get("User", obj_id).id, obj_id)


if __name__ == "__main__":
    unittest.main()
