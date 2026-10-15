#!/usr/bin/python3
"""Defines HBNBCommand, the entry point of the HBnB command interpreter."""
import cmd


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


if __name__ == '__main__':
    HBNBCommand().cmdloop()
