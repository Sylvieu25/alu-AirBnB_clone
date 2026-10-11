# AirBnB Clone - The Console

## Description

This project is the first step of building a full-stack clone of the AirBnB web application (HBnB).
In this first part, we build the **backend foundation**:

- A `BaseModel` parent class that handles the initialization, serialization and deserialization of all future instances.
- A simple serialization/deserialization flow: **Instance <-> Dictionary <-> JSON string <-> file**.
- Model classes used across the project: `User`, `State`, `City`, `Amenity`, `Place` and `Review`, all inheriting from `BaseModel`.
- An abstracted storage engine (`FileStorage`) that saves objects to a JSON file and reloads them.
- A command interpreter to create, retrieve, update and delete those objects.
- Unit tests that validate all classes and the storage engine.

Later parts of the project reuse this foundation for HTML/CSS templating, MySQL storage, a RESTful API and front-end integration.

## The Command Interpreter

The command interpreter (`console.py`) is a shell built with Python's `cmd` module. It is limited to one use case: managing the objects of the project. With it you can:

- Create a new object (e.g. a new `User` or a new `Place`)
- Retrieve an object from a file
- Do operations on objects (count, show all, etc.)
- Update the attributes of an object
- Destroy an object

### How to start it

Clone the repository and run the console from its root:

```bash
$ git clone https://github.com/Sylvieu25/alu-AirBnB_clone.git
$ cd alu-AirBnB_clone
$ ./console.py
(hbnb)
```

### How to use it

The console works in **interactive mode**:

```bash
$ ./console.py
(hbnb) help

Documented commands (type help <topic>):
========================================
EOF  all  count  create  destroy  help  quit  show  update

(hbnb) quit
$
```

And in **non-interactive mode**:

```bash
$ echo "help" | ./console.py
(hbnb)

Documented commands (type help <topic>):
========================================
EOF  all  count  create  destroy  help  quit  show  update
(hbnb)
$
```

### Available commands

| Command | Usage | Description |
|---|---|---|
| `create` | `create <class>` | Creates a new instance, saves it to the JSON file and prints its `id` |
| `show` | `show <class> <id>` | Prints the string representation of an instance |
| `destroy` | `destroy <class> <id>` | Deletes an instance and saves the change |
| `all` | `all` or `all <class>` | Prints all instances, or all instances of a class |
| `update` | `update <class> <id> <attribute> "<value>"` | Adds or updates an attribute of an instance |
| `count` | `<class>.count()` | Prints the number of instances of a class |
| `help` | `help` or `help <command>` | Shows available commands or help for a command |
| `quit` / `EOF` | `quit` or `Ctrl+D` | Exits the console |

Supported classes: `BaseModel`, `User`, `State`, `City`, `Amenity`, `Place`, `Review`.

The console also supports the `<class name>.<command>()` syntax:

```
(hbnb) User.all()
(hbnb) User.count()
(hbnb) User.show("<id>")
(hbnb) User.destroy("<id>")
(hbnb) User.update("<id>", "<attribute name>", "<attribute value>")
(hbnb) User.update("<id>", {"first_name": "John", "age": 89})
```

### Examples

```
(hbnb) create User
49faff9a-6318-451f-87b6-910505c55907
(hbnb) show User 49faff9a-6318-451f-87b6-910505c55907
[User] (49faff9a-6318-451f-87b6-910505c55907) {'id': '49faff9a-6318-451f-87b6-910505c55907', 'created_at': datetime.datetime(2026, 10, 11, 13, 30, 2, 123456), 'updated_at': datetime.datetime(2026, 10, 11, 13, 30, 2, 123456)}
(hbnb) update User 49faff9a-6318-451f-87b6-910505c55907 first_name "Betty"
(hbnb) User.count()
1
(hbnb) destroy User 49faff9a-6318-451f-87b6-910505c55907
(hbnb) show User 49faff9a-6318-451f-87b6-910505c55907
** no instance found **
(hbnb) quit
```

## Project Structure

```
alu-AirBnB_clone/
├── AUTHORS
├── README.md
├── console.py
├── models/
│   ├── __init__.py
│   ├── base_model.py
│   ├── user.py
│   ├── state.py
│   ├──