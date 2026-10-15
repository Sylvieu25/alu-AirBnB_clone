#!/usr/bin/python3
"""Defines HBNBCommand, the entry point of the HBnB command interpreter."""
import ast
import cmd
import re
import shlex

from models import storage


def parse(arg):
    """Split a command line into arguments, keeping quoted strings whole."""
    try:
        return shlex.split(arg)
    except ValueError:
        return arg.split()


def cast_value(value, current=None):
    """Cast a string value to the type of current, or to int/float/str."""
    if current is not None and type(current) in (int, float, str):
        try:
            return type(current)(value)
        except ValueError:
            return value
    for kind in (int, float):
        try:
            return kind(value)
        except ValueError:
            pass
    return value


class HBNBCommand(cmd.Cmd):
    """Command interpreter used to manage the HBnB objects."""

    prompt = "(hbnb) "

    def do_quit(self, arg):
        """Quit command to exit the program
        """
        return True

    def do_EOF(self, arg):
        """EOF command to exit the program
        """
        print("")
        return True

    def emptyline(self):
        """Do nothing when an empty line is entered."""
        pass

    def default(self, line):
        """Handle the <class name>.<method>(<args>) syntax.

        Supported methods: all(), count(), show(<id>), destroy(<id>),
        update(<id>, <attribute name>, <attribute value>) and
        update(<id>, <dictionary representation>).
        """
        match = re.fullmatch(r"\s*(\w*)\.(\w+)\((.*)\)\s*", line)
        if match is None:
            print("*** Unknown syntax: {}".format(line))
            return False
        cls_name, method, args = match.groups()
        if method == "all":
            return self.do_all(cls_name)
        if method == "count":
            return self.count(cls_name)
        if method in ("show", "destroy"):
            arg = "{} {}".format(cls_name, args.replace(",", " "))
            return getattr(self, "do_" + method)(arg)
        if method == "update":
            return self.update_from_call(cls_name, args)
        print("*** Unknown syntax: {}".format(line))
        return False

    def count(self, cls_name):
        """Print the number of instances of a class."""
        if not cls_name:
            print("** class name missing **")
        elif cls_name not in storage.classes():
            print("** class doesn't exist **")
        else:
            print(sum(1 for obj in storage.all().values()
                      if type(obj).__name__ == cls_name))

    def update_from_call(self, cls_name, args):
        """Run update with the arguments of <class name>.update(...)."""
        match = re.fullmatch(r"\s*[\"']?([^\"',]*)[\"']?\s*,\s*(\{.*\})\s*",
                             args)
        if match is None:
            return self.do_update(
                "{} {}".format(cls_name, args.replace(",", " ")))
        obj_id, dict_repr = match.groups()
        key = self.get_instance_key([cls_name, obj_id] if cls_name
                                    else [])
        if key is None:
            return
        try:
            attributes = ast.literal_eval(dict_repr)
        except (ValueError, SyntaxError):
            print("** value missing **")
            return
        obj = storage.all()[key]
        for name, value in attributes.items():
            if name in ("id", "created_at", "updated_at"):
                continue
            current = getattr(obj, name, None)
            if isinstance(value, str):
                value = cast_value(value, current)
            setattr(obj, name, value)
        obj.save()

    def get_instance_key(self, args):
        """Check class name and id in args and return the storage key.

        Print the matching error message and return None on any error.
        """
        if len(args) == 0:
            print("** class name missing **")
            return None
        if args[0] not in storage.classes():
            print("** class doesn't exist **")
            return None
        if len(args) == 1:
            print("** instance id missing **")
            return None
        key = "{}.{}".format(args[0], args[1])
        if key not in storage.all():
            print("** no instance found **")
            return None
        return key

    def do_create(self, arg):
        """Create a new instance, save it and print its id.
        Usage: create <class name>
        """
        args = parse(arg)
        if len(args) == 0:
            print("** class name missing **")
            return
        classes = storage.classes()
        if args[0] not in classes:
            print("** class doesn't exist **")
            return
        obj = classes[args[0]]()
        obj.save()
        print(obj.id)

    def do_show(self, arg):
        """Print the string representation of an instance.
        Usage: show <class name> <id>
        """
        key = self.get_instance_key(parse(arg))
        if key is not None:
            print(storage.all()[key])

    def do_destroy(self, arg):
        """Delete an instance and save the change into the JSON file.
        Usage: destroy <class name> <id>
        """
        key = self.get_instance_key(parse(arg))
        if key is not None:
            del storage.all()[key]
            storage.save()

    def do_all(self, arg):
        """Print all instances, or all instances of a class.
        Usage: all or all <class name>
        """
        args = parse(arg)
        if len(args) > 0 and args[0] not in storage.classes():
            print("** class doesn't exist **")
            return
        print([str(obj) for obj in storage.all().values()
               if len(args) == 0 or type(obj).__name__ == args[0]])

    def do_update(self, arg):
        """Add or update an attribute of an instance and save it.
        Usage: update <class name> <id> <attribute name> "<attribute value>"
        """
        args = parse(arg)
        key = self.get_instance_key(args)
        if key is None:
            return
        if len(args) == 2:
            print("** attribute name missing **")
            return
        if len(args) == 3:
            print("** value missing **")
            return
        obj = storage.all()[key]
        name = args[2]
        if name in ("id", "created_at", "updated_at"):
            return
        setattr(obj, name, cast_value(args[3], getattr(obj, name, None)))
        obj.save()


if __name__ == '__main__':
    HBNBCommand().cmdloop()
