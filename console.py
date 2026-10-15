#!/usr/bin/python3
"""Defines HBNBCommand, the entry point of the HBnB command interpreter."""
import cmd
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
