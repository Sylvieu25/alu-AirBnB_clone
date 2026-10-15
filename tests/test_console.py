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
CLASSES = ["BaseModel", "User", "State", "City",
           "Amenity", "Place", "Review"]


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


def run(command):
    """Run one console command and return what it printed, stripped."""
    with patch("sys.stdout", new=StringIO()) as output:
        HBNBCommand().onecmd(command)
    return output.getvalue().strip()


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

    def create(self, cls_name):
        """Create an instance with the console and return its id."""
        return run("create {}".format(cls_name))


class TestConsoleBasics(ConsoleTestCase):
    """Tests for the prompt, quit, EOF, empty lines and help."""

    def test_prompt(self):
        """The prompt is '(hbnb) '."""
        self.assertEqual(HBNBCommand.prompt, "(hbnb) ")

    def test_quit_returns_true(self):
        """quit stops the command loop."""
        with patch("sys.stdout", new=StringIO()):
            self.assertTrue(HBNBCommand().onecmd("quit"))

    def test_eof_returns_true_and_prints_newline(self):
        """EOF stops the command loop and prints a new line."""
        with patch("sys.stdout", new=StringIO()) as output:
            self.assertTrue(HBNBCommand().onecmd("EOF"))
        self.assertEqual(output.getvalue(), "\n")

    def test_empty_line(self):
        """An empty line prints nothing."""
        self.assertEqual(run(""), "")
        self.assertEqual(run("   "), "")

    def test_empty_line_does_not_repeat_last_command(self):
        """An empty line after a command does not run it again."""
        with patch("sys.stdout", new=StringIO()) as output:
            console = HBNBCommand()
            console.onecmd("help quit")
            first = output.getvalue()
            console.onecmd("")
        self.assertIn("Quit command", first)
        self.assertEqual(output.getvalue(), first)

    def test_help_lists_commands(self):
        """help lists every documented command."""
        output = run("help")
        for command in ("EOF", "all", "create", "destroy", "help",
                        "quit", "show", "update"):
            self.assertIn(command, output)

    def test_help_quit(self):
        """help quit prints the quit docstring."""
        self.assertEqual(run("help quit"), "Quit command to exit the program")

    def test_help_eof(self):
        """help EOF prints the EOF docstring."""
        self.assertEqual(run("help EOF"), "EOF command to exit the program")

    def test_help_each_command(self):
        """Every command has a help message."""
        for command in ("create", "show", "destroy", "all", "update"):
            self.assertNotEqual(run("help {}".format(command)), "")
            self.assertNotIn("No help", run("help {}".format(command)))

    def test_unknown_command(self):
        """An unknown command prints an Unknown syntax message."""
        self.assertEqual(run("hello"), "*** Unknown syntax: hello")

    def test_unknown_method(self):
        """An unknown <class>.<method>() prints Unknown syntax."""
        self.assertEqual(run("User.fly()"), "*** Unknown syntax: User.fly()")


class TestConsoleCreate(ConsoleTestCase):
    """Tests for the create command."""

    def test_missing_class(self):
        """create without a class prints class name missing."""
        self.assertEqual(run("create"), "** class name missing **")

    def test_invalid_class(self):
        """create with an unknown class prints class doesn't exist."""
        self.assertEqual(run("create MyModel"), "** class doesn't exist **")

    def test_create_every_class(self):
        """create works for every class and stores the new object."""
        for cls_name in CLASSES:
            obj_id = self.create(cls_name)
            self.assertEqual(len(obj_id), 36)
            key = "{}.{}".format(cls_name, obj_id)
            self.assertIn(key, models.storage.all())
            self.assertEqual(
                type(models.storage.all()[key]).__name__, cls_name)

    def test_create_saves_to_file(self):
        """create writes the new object to the JSON file."""
        obj_id = self.create("User")
        with open(FILE, "r", encoding="utf-8") as f:
            self.assertIn("User.{}".format(obj_id), f.read())

    def test_create_unique_ids(self):
        """Two create commands give two different ids."""
        self.assertNotEqual(self.create("User"), self.create("User"))


class TestConsoleShow(ConsoleTestCase):
    """Tests for the show command and <class>.show()."""

    def test_missing_class(self):
        """show without a class prints class name missing."""
        self.assertEqual(run("show"), "** class name missing **")
        self.assertEqual(run(".show()"), "** class name missing **")

    def test_invalid_class(self):
        """show with an unknown class prints class doesn't exist."""
        self.assertEqual(run("show MyModel"), "** class doesn't exist **")
        self.assertEqual(run("MyModel.show()"), "** class doesn't exist **")

    def test_missing_id(self):
        """show without an id prints instance id missing."""
        self.assertEqual(run("show User"), "** instance id missing **")
        self.assertEqual(run("User.show()"), "** instance id missing **")

    def test_no_instance(self):
        """show with an unknown id prints no instance found."""
        self.assertEqual(run("show User 1234"), "** no instance found **")
        self.assertEqual(run('User.show("1234")'), "** no instance found **")

    def test_show_every_class(self):
        """show prints the string representation of the instance."""
        for cls_name in CLASSES:
            obj_id = self.create(cls_name)
            obj = models.storage.all()["{}.{}".format(cls_name, obj_id)]
            self.assertEqual(run("show {} {}".format(cls_name, obj_id)),
                             str(obj))

    def test_dot_show_every_class(self):
        """<class>.show(<id>) prints the same as show <class> <id>."""
        for cls_name in CLASSES:
            obj_id = self.create(cls_name)
            self.assertEqual(
                run('{}.show("{}")'.format(cls_name, obj_id)),
                run("show {} {}".format(cls_name, obj_id)))

    def test_show_wrong_class_for_id(self):
        """An id only matches the class it was created with."""
        obj_id = self.create("User")
        self.assertEqual(run("show Place {}".format(obj_id)),
                         "** no instance found **")


class TestConsoleDestroy(ConsoleTestCase):
    """Tests for the destroy command and <class>.destroy()."""

    def test_missing_class(self):
        """destroy without a class prints class name missing."""
        self.assertEqual(run("destroy"), "** class name missing **")
        self.assertEqual(run(".destroy()"), "** class name missing **")

    def test_invalid_class(self):
        """destroy with an unknown class prints class doesn't exist."""
        self.assertEqual(run("destroy MyModel"), "** class doesn't exist **")
        self.assertEqual(run("MyModel.destroy()"),
                         "** class doesn't exist **")

    def test_missing_id(self):
        """destroy without an id prints instance id missing."""
        self.assertEqual(run("destroy User"), "** instance id missing **")
        self.assertEqual(run("User.destroy()"), "** instance id missing **")

    def test_no_instance(self):
        """destroy with an unknown id prints no instance found."""
        self.assertEqual(run("destroy User 1234"), "** no instance found **")
        self.assertEqual(run('User.destroy("1234")'),
                         "** no instance found **")

    def test_destroy_every_class(self):
        """destroy removes the instance from storage and the file."""
        for cls_name in CLASSES:
            obj_id = self.create(cls_name)
            key = "{}.{}".format(cls_name, obj_id)
            self.assertEqual(run("destroy {} {}".format(cls_name, obj_id)),
                             "")
            self.assertNotIn(key, models.storage.all())
            with open(FILE, "r", encoding="utf-8") as f:
                self.assertNotIn(key, f.read())

    def test_dot_destroy_every_class(self):
        """<class>.destroy(<id>) removes the instance."""
        for cls_name in CLASSES:
            obj_id = self.create(cls_name)
            run('{}.destroy("{}")'.format(cls_name, obj_id))
            self.assertNotIn("{}.{}".format(cls_name, obj_id),
                             models.storage.all())

    def test_show_after_destroy(self):
        """show after destroy prints no instance found."""
        obj_id = self.create("User")
        run("destroy User {}".format(obj_id))
        self.assertEqual(run("show User {}".format(obj_id)),
                         "** no instance found **")


class TestConsoleAll(ConsoleTestCase):
    """Tests for the all command and <class>.all()."""

    def test_invalid_class(self):
        """all with an unknown class prints class doesn't exist."""
        self.assertEqual(run("all MyModel"), "** class doesn't exist **")
        self.assertEqual(run("MyModel.all()"), "** class doesn't exist **")

    def test_empty(self):
        """all with no objects prints an empty list."""
        self.assertEqual(run("all"), "[]")
        self.assertEqual(run("all User"), "[]")

    def test_all_objects(self):
        """all prints every object, of every class."""
        for cls_name in CLASSES:
            self.create(cls_name)
        output = run("all")
        for cls_name in CLASSES:
            self.assertIn("[{}]".format(cls_name), output)

    def test_all_by_class(self):
        """all <class> prints only the objects of that class."""
        self.create("User")
        self.create("Place")
        output = run("all User")
        self.assertIn("[User]", output)
        self.assertNotIn("[Place]", output)

    def test_all_prints_list_of_strings(self):
        """all prints a list of the string representations."""
        obj_id = self.create("User")
        obj = models.storage.all()["User.{}".format(obj_id)]
        self.assertEqual(run("all User"), str([str(obj)]))

    def test_dot_all_every_class(self):
        """<class>.all() prints the same as all <class>."""
        for cls_name in CLASSES:
            self.create(cls_name)
        for cls_name in CLASSES:
            self.assertEqual(run("{}.all()".format(cls_name)),
                             run("all {}".format(cls_name)))


class TestConsoleCount(ConsoleTestCase):
    """Tests for <class>.count()."""

    def test_missing_class(self):
        """.count() without a class prints class name missing."""
        self.assertEqual(run(".count()"), "** class name missing **")

    def test_invalid_class(self):
        """<class>.count() with an unknown class prints an error."""
        self.assertEqual(run("MyModel.count()"), "** class doesn't exist **")

    def test_count_zero(self):
        """count is 0 when no instance of the class exists."""
        for cls_name in CLASSES:
            self.assertEqual(run("{}.count()".format(cls_name)), "0")

    def test_count_by_class(self):
        """count only counts the instances of the given class."""
        self.create("User")
        self.create("User")
        self.create("State")
        self.assertEqual(run("User.count()"), "2")
        self.assertEqual(run("State.count()"), "1")
        self.assertEqual(run("Place.count()"), "0")

    def test_count_after_destroy(self):
        """count goes down after destroy."""
        obj_id = self.create("User")
        self.create("User")
        run('User.destroy("{}")'.format(obj_id))
        self.assertEqual(run("User.count()"), "1")


class TestConsoleUpdate(ConsoleTestCase):
    """Tests for the update command and <class>.update()."""

    def test_missing_class(self):
        """update without a class prints class name missing."""
        self.assertEqual(run("update"), "** class name missing **")
        self.assertEqual(run(".update()"), "** class name missing **")

    def test_invalid_class(self):
        """update with an unknown class prints class doesn't exist."""
        self.assertEqual(run("update MyModel"), "** class doesn't exist **")
        self.assertEqual(run("MyModel.update()"),
                         "** class doesn't exist **")

    def test_missing_id(self):
        """update without an id prints instance id missing."""
        self.assertEqual(run("update User"), "** instance id missing **")
        self.assertEqual(run("User.update()"), "** instance id missing **")

    def test_no_instance(self):
        """update with an unknown id prints no instance found."""
        self.assertEqual(run("update User 1234"), "** no instance found **")
        self.assertEqual(run('User.update("1234")'),
                         "** no instance found **")
        self.assertEqual(run('User.update("1234", {"a": 1})'),
                         "** no instance found **")

    def test_missing_attribute_name(self):
        """update without an attribute prints attribute name missing."""
        obj_id = self.create("User")
        self.assertEqual(run("update User {}".format(obj_id)),
                         "** attribute name missing **")
        self.assertEqual(run('User.update("{}")'.format(obj_id)),
                         "** attribute name missing **")

    def test_missing_value(self):
        """update without a value prints value missing."""
        obj_id = self.create("User")
        self.assertEqual(run("update User {} first_name".format(obj_id)),
                         "** value missing **")
        self.assertEqual(
            run('User.update("{}", "first_name")'.format(obj_id)),
            "** value missing **")

    def test_update_string_with_spaces(self):
        """A quoted value with spaces is stored whole."""
        obj_id = self.create("User")
        run('update User {} first_name "Betty Holberton"'.format(obj_id))
        obj = models.storage.all()["User.{}".format(obj_id)]
        self.assertEqual(obj.first_name, "Betty Holberton")

    def test_update_casts_to_attribute_type(self):
        """Values are cast to the type of the class attribute."""
        obj_id = self.create("Place")
        run("update Place {} number_rooms 4".format(obj_id))
        run("update Place {} latitude 37.77".format(obj_id))
        run("update Place {} name 123".format(obj_id))
        obj = models.storage.all()["Place.{}".format(obj_id)]
        self.assertEqual(obj.number_rooms, 4)
        self.assertIs(type(obj.number_rooms), int)
        self.assertEqual(obj.latitude, 37.77)
        self.assertIs(type(obj.latitude), float)
        self.assertEqual(obj.name, "123")

    def test_update_new_attribute_types(self):
        """New attributes are cast to int, float or kept as str."""
        obj_id = self.create("BaseModel")
        run("update BaseModel {} age 89".format(obj_id))
        run("update BaseModel {} score 3.5".format(obj_id))
        run("update BaseModel {} nick Bob".format(obj_id))
        obj = models.storage.all()["BaseModel.{}".format(obj_id)]
        self.assertEqual(obj.age, 89)
        self.assertEqual(obj.score, 3.5)
        self.assertEqual(obj.nick, "Bob")

    def test_update_only_first_attribute(self):
        """Extra arguments after the first value are ignored."""
        obj_id = self.create("User")
        run('update User {} email "a@b.c" first_name "Betty"'.format(obj_id))
        obj = models.storage.all()["User.{}".format(obj_id)]
        self.assertEqual(obj.email, "a@b.c")
        self.assertNotIn("first_name", obj.__dict__)

    def test_update_saves_to_file(self):
        """update writes the new value to the JSON file."""
        obj_id = self.create("User")
        run('update User {} first_name "Betty"'.format(obj_id))
        with open(FILE, "r", encoding="utf-8") as f:
            self.assertIn('"first_name": "Betty"', f.read())

    def test_update_changes_updated_at(self):
        """update moves updated_at forward."""
        obj_id = self.create("User")
        obj = models.storage.all()["User.{}".format(obj_id)]
        before = obj.updated_at
        run('update User {} first_name "Betty"'.format(obj_id))
        self.assertGreaterEqual(obj.updated_at, before)

    def test_dot_update_attribute(self):
        """<class>.update(<id>, <name>, <value>) sets the attribute."""
        for cls_name in CLASSES:
            obj_id = self.create(cls_name)
            run('{}.update("{}", "nick", "John Doe")'.format(
                cls_name, obj_id))
            obj = models.storage.all()["{}.{}".format(cls_name, obj_id)]
            self.assertEqual(obj.nick, "John Doe")

    def test_dot_update_int_value(self):
        """<class>.update() casts a number value."""
        obj_id = self.create("Place")
        run('Place.update("{}", "max_guest", 6)'.format(obj_id))
        obj = models.storage.all()["Place.{}".format(obj_id)]
        self.assertEqual(obj.max_guest, 6)

    def test_dot_update_dict(self):
        """<class>.update(<id>, <dict>) sets every attribute."""
        for cls_name in CLASSES:
            obj_id = self.create(cls_name)
            run('{}.update("{}", {{"first_name": "John", "age": 89}})'
                .format(cls_name, obj_id))
            obj = models.storage.all()["{}.{}".format(cls_name, obj_id)]
            self.assertEqual(obj.first_name, "John")
            self.assertEqual(obj.age, 89)

    def test_dot_update_dict_single_quotes(self):
        """A dictionary with single quotes is accepted."""
        obj_id = self.create("User")
        run("User.update('{}', {{'last_name': 'Doe'}})".format(obj_id))
        obj = models.storage.all()["User.{}".format(obj_id)]
        self.assertEqual(obj.last_name, "Doe")

    def test_dot_update_dict_casts_strings(self):
        """String values in the dict are cast to the attribute type."""
        obj_id = self.create("Place")
        run('Place.update("{}", {{"number_rooms": "3"}})'.format(obj_id))
        obj = models.storage.all()["Place.{}".format(obj_id)]
        self.assertEqual(obj.number_rooms, 3)

    def test_id_not_updated(self):
        """id, created_at and updated_at cannot be changed."""
        obj_id = self.create("User")
        run("update User {} id 1234".format(obj_id))
        run('User.update("{}", {{"id": "1234"}})'.format(obj_id))
        self.assertIn("User.{}".format(obj_id), models.storage.all())
        obj = models.storage.all()["User.{}".format(obj_id)]
        self.assertEqual(obj.id, obj_id)


if __name__ == "__main__":
    unittest.main()
