# AirBnB Clone

## Description

This project is the first step of building a full-stack clone of the AirBnB web application (HBnB).
In this first part, we build the **backend foundation**:

- A `BaseModel` parent class that handles the initialization, serialization and deserialization of all instances.
- A serialization/deserialization flow: **Instance <-> Dictionary <-> JSON string <-> file**.
- Model classes used across the project: `User`, `State`, `City`, `Amenity`, `Place` and `Review`, all inheriting from `BaseModel`.
- A storage engine (`FileStorage`) that saves objects to a JSON file and reloads them.
- A command interpreter to create, retrieve, update and delete those objects.
- Unit tests that validate all classes and the storage engine.

Later parts of the project reuse this foundation for HTML/CSS templating, MySQL storage, a RESTful API and front-end integration.

## The Command Interpreter

The command interpreter (`console.py`) is a shell built with Python's `cmd` module. It is limited to one use case: managing the objects of the project. With it you can:

- Create a new object (e.g. a new `User` or a new `Place`)
- Retrieve an object from the JSON file
- List all objects, or all objects of a class
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
EOF  all  create  destroy  help  quit  show  update

(hbnb) quit
$
```

And in **non-interactive mode**:

```bash
$ echo "help" | ./console.py
(hbnb)
Documented commands (type help <topic>):
========================================
EOF  all  create  destroy  help  quit  show  update

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
| `help` | `help` or `help <command>` | Shows available commands or help for a command |
| `quit` / `EOF` | `quit` or `Ctrl+D` | Exits the console |

Supported classes: `BaseModel`, `User`, `State`, `City`, `Amenity`, `Place`, `Review`.

Values passed to `update` are cast to the attribute's type: `update Place <id> max_guest 6` stores the integer `6`.

### Examples

```
(hbnb) create User
49faff9a-6318-451f-87b6-910505c55907
(hbnb) show User 49faff9a-6318-451f-87b6-910505c55907
[User] (49faff9a-6318-451f-87b6-910505c55907) {'id': '49faff9a-6318-451f-87b6-910505c55907', 'created_at': datetime.datetime(2026, 10, 15, 21, 30, 2, 123456), 'updated_at': datetime.datetime(2026, 10, 15, 21, 30, 2, 123456)}
(hbnb) update User 49faff9a-6318-451f-87b6-910505c55907 first_name "Betty"
(hbnb) all User
["[User] (49faff9a-6318-451f-87b6-910505c55907) {'id': '49faff9a-6318-451f-87b6-910505c55907', 'created_at': datetime.datetime(2026, 10, 15, 21, 30, 2, 123456), 'updated_at': datetime.datetime(2026, 10, 15, 21, 30, 9, 654321), 'first_name': 'Betty'}"]
(hbnb) destroy User 49faff9a-6318-451f-87b6-910505c55907
(hbnb) show User 49faff9a-6318-451f-87b6-910505c55907
** no instance found **
(hbnb) create MyModel
** class doesn't exist **
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
│   ├── city.py
│   ├── amenity.py
│   ├── place.py
│   ├── review.py
│   └── engine/
│       ├── __init__.py
│       └── file_storage.py
├── tests/
│   └── test_models/
│       ├── test_base_model.py
│       ├── test_user.py
│       ├── test_state.py
│       ├── test_city.py
│       ├── test_amenity.py
│       ├── test_place.py
│       ├── test_review.py
│       └── test_engine/
│           └── test_file_storage.py
└── web_static/
    ├── 0-index.html
    ├── 1-index.html
    ├── 2-index.html
    ├── 3-index.html
    ├── styles/
    └── images/
```

## Running the Tests

```bash
$ python3 -m unittest discover tests
```

Tests also pass in non-interactive mode:

```bash
$ echo "python3 -m unittest discover tests" | bash
```

## Web Static

The `web_static` folder holds the static front end of the project: the HTML/CSS pages that will later be turned into dynamic templates. The pages are built step by step from mockups, starting with inline styles and moving to external stylesheets.

Constraints:

- No JavaScript
- No `img`, `embed` or `iframe` tags (images are applied as CSS backgrounds)
- No `id` selectors and no `!important` in CSS
- All CSS files in `web_static/styles/`, all images in `web_static/images/`
- All markup must pass [W3C validation](https://validator.w3.org/)

| File | Description |
|------|-------------|
| `0-index.html` | Header and footer using inline styles |
| `1-index.html` | Header and footer using a `style` tag in the `head` |
| `2-index.html` | Header and footer using external CSS files in `styles/` |
| `3-index.html` | Header with logo, footer with text, favicon, using external CSS files |

## Author

See the [AUTHORS](./AUTHORS) file.
