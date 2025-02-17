# Terminal GUI

Terminal GUI is a Python package for creating terminal-based menu systems and configuration files.

## Features

- Create a menu based on a config file (TOML or YAML).
- Create a config file based on user input.
- Navigate the menu using arrow keys or shortcuts.

## Installation

To install the package, use the following command:

```bash
uv add terminal-gui
```

## Usage

### Creating a Menu

```python
from terminal_gui.menu import menu

title = "Main Menu"
choices = ["Option 1", "Option 2", "Option 3"]
menu(title, choices)
```

### Loading and Saving Configurations

```python
from terminal_gui.config import load_config, save_config

config_data = load_config('config.toml')
save_config('config.toml', config_data)
```

## Running Tests

To run the tests, use the following command:

```bash
pytest